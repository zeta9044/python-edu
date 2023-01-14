import pandas as pd
import os
import math
import xml.etree.ElementTree as ET
from rtde.security import DecryptFile
from rtde.util import convNoneToEmptyString, euc2utf, set_xmldir, make_cdata, alt_char, read_qtrack_table_list, attach_schema_name, get_transform_dic, tranform_postgres_to_oracle, set_log, create_engine
import logging
import logging.config
import concurrent.futures
import time
import argparse
import copy
import sqlalchemy as sa
from functools import reduce
# 상수선언
XML_TYPE = """<?xml version="1.0" encoding="UTF-8"?>\n"""


# 프로그램쿼리

# 프로그램쿼리
def rtde_program_query(type: str, ais8801_table_name: str, ais8800_table_name: str):
    program_group_query = f"select pgm_grp_id, pgm_grp_nm from {ais8801_table_name} where lia_type_cd = '0' and aval_ed_dt = '99991231235959' order by pgm_grp_id,exec_ord_no"
    program_query = f"select a.pgm_id, a.pgm_grp_id, b.pgm_grp_nm, b.exec_ord_no, a.pgm_src from {ais8800_table_name} a, {ais8801_table_name} b where a.aval_ed_dt = '99991231235959' and a.lia_type_cd = '0' and b.aval_ed_dt = '99991231235959' and b.lia_type_cd = '0' and a.pgm_grp_id = b.pgm_grp_id and b.pgm_grp_nm = %s order by b.exec_ord_no, a.pgm_grp_id, a.exec_ord_no"
    program_query_lia = f"select a.pgm_id, a.pgm_grp_id, a.exec_ord_no, a.pgm_src from {ais8800_table_name} a where a.aval_ed_dt = '99991231235959' and a.lia_type_cd != '0' order by a.pgm_grp_id, a.exec_ord_no"
    return (lambda t: (program_group_query, program_query) if t == 'was' else program_query_lia if t == 'lia' else print("type은 was 또는 lia") and exit())(type)


print(rtde_program_query('was', 'ais8801', 'ais8800'))
print(rtde_program_query('lia', 'ais8801', 'ais8800'))

# 프로그램메타쿼리


def rtde_group_meta_query(type: str, ais8801_table_name: str):
    type_val = {'was': '=', 'lia': '!='}
    query = f"select pgm_grp_id, pgm_grp_nm, pgm_grp_desc, lia_type_cd, exec_ord_no, reanly_exec_yn, exec_cond_yn, exec_pgm_id, del_yn from {ais8801_table_name} where lia_type_cd {type_val.get(type,'')} '0' and aval_ed_dt = '99991231235959' order by pgm_grp_id,exec_ord_no"
    return query if type in type_val else print("type은 was 또는 lia") and exit()


print(rtde_group_meta_query('was', 'ais8801'))
print(rtde_group_meta_query('lia', 'ais8801'))


# 스키마 및 변환결과
def trans(s: str, args: argparse.Namespace):
    input = copy.copy(s)
    if args.transform_db is not None:
        input = tranform_postgres_to_oracle(input, get_transform_dic())
    if args.schema_name is not None:
        input = attach_schema_name(
            input, args.schema_name, read_qtrack_table_list())
    return input

# was xml 만들기


def make_was_xml(was_xml_path: str, was_group_query: str, was_program_query: str, engine: sa.engine, logger: logging.Logger, args: argparse.Namespace):

    logger.info('was xml 만들기 시작')

    try:

        was_rtde_group_df = pd.read_sql_query(was_group_query, con=engine)

        for idx in range(len(was_rtde_group_df)):
            # pgm_grp_id별로 xml구성요소 읽기
            was_rtde_id_df = pd.read_sql_query(
                was_program_query, con=engine, params=tuple(was_rtde_group_df.values[idx]))
            temp_list = str(tuple(was_rtde_group_df.values[idx])[
                            0]).replace('\\', '/').split('/')
            file_name = temp_list[len(temp_list)-1]
            logger.debug(file_name+'%s', '생성...')

            # XML헤더/풋터
            XML_TYPE = """<?xml version="1.0" encoding="UTF-8"?>\n"""
            xml_doc_type = """<!DOCTYPE mapper
            PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
            "http://mybatis.org/dtd/mybatis-3-mapper.dtd">\n"""
            xml_header = """<mapper namespace="%s" >""" % tuple(
                was_rtde_group_df.values[idx])[1]
            xml_footer = "</mapper>"

            # XML파일생성
            with open(was_xml_path+file_name, 'w', encoding='utf-8') as file:
                file.write(xml_header)
                for inner_idx in range(len(was_rtde_id_df)):
                    s = str(DecryptFile.decrypt(
                        was_rtde_id_df['pgm_src'][inner_idx]))
                    s = trans(s, args)
                    was_rtde_id_df.loc[inner_idx, 'pgm_src'] = alt_char(s)
                    file.write(was_rtde_id_df['pgm_src'][inner_idx])
                file.write(xml_footer)

            # XML파일 beautify
            with open(was_xml_path+file_name, 'r', encoding='utf-8') as file:
                element = ET.XML(file.read())
                ET.indent(element)
            with open(was_xml_path+file_name, 'w', encoding='utf-8') as file:
                file.write(XML_TYPE)
                file.write(xml_doc_type)
                file.write(ET.tostring(element, encoding='unicode'))
    except Exception as e:
        logger.exception(e)

    logger.info('was xml 만들기 종료')

    return len(was_rtde_group_df)


def process_group_row(acc, index: int, row: pd.Series) -> list:
    row['pgm_grp_desc'] = make_cdata(
        str(DecryptFile.decrypt(row['pgm_grp_desc'])))
    acc.append((row['pgm_grp_id'], row['pgm_grp_nm'], row['pgm_grp_desc'], row['lia_type_cd'], math.trunc(row['exec_ord_no']),
                row['reanly_exec_yn'], row['exec_cond_yn'], convNoneToEmptyString(row['exec_pgm_id']), row['del_yn']))
    return acc


def write_group_tag(file, row: tuple):
    file.write("""<rtde_grp """)
    file.write("pgm_grp_id=\""+row[0].replace('\\', '/')+"\" ")
    file.write("pgm_grp_nm=\""+row[1]+"\" ")
    file.write("lia_type_cd=\""+row[3]+"\" ")
    file.write("exec_ord_no=\""+str(math.trunc(row[4]))+"\" ")
    file.write("reanly_exec_yn=\""+row[5]+"\" ")
    file.write("exec_cond_yn=\""+row[6]+"\" ")
    file.write("exec_pgm_id=\""+convNoneToEmptyString(row[7])+"\" ")
    file.write("del_yn=\""+row[8]+"\" ")
    file.write(""" >"""+row[2]+'</rtde_grp>\n')
    return file


def process_program_row(acc, index: int, row: pd.Series) -> list:
    row['pgm_desc'] = make_cdata(str(DecryptFile.decrypt(row['pgm_desc'])))
    acc.append((row['pgm_id'], row['pgm_grp_id'], row['lia_type_cd'], row['db_type_cd'], math.trunc(row['pgm_nm']),
                row['exec_ord_no'], row['src_type_cd'], row['sql_type_cd'], row['pgm_desc'], row['data_maker'], convNoneToEmptyString(row['common_exec_yn']), row['use_type_cd'], row['del_yn']))
    return acc


def write_program_tag(file,  row: tuple) :
    file.write("""<rtde_pgm """)
    file.write("pgm_id=\""+row[0]+"\" ")
    file.write("pgm_grp_id=\""+row[1].replace('\\', '/')+"\" ")
    file.write("lia_type_cd=\""+row[2]+"\" ")
    file.write("db_type_cd=\""+row[3]+"\" ")
    file.write("pgm_nm=\""+row[4]+"\" ")
    file.write("exec_ord_no=\""+str(math.trunc(row[5]))+"\" ")
    file.write("src_type_cd=\""+row[6]+"\" ")
    file.write("sql_type_cd=\""+row[7]+"\" ")
    file.write("data_maker=\""+row[9]+"\" ")
    file.write("common_exec_yn=\""+convNoneToEmptyString(row[10])+"\" ")
    file.write("use_type_cd=\""+row[11]+"\" ")
    file.write("del_yn=\""+row[12]+"\" ")
    file.write(""" >"""+row[8]+'</rtde_pgm>\n')

# was meta xml 만들기


def make_was_meta_xml(was_xml_path, was_group_meta_query, was_program_meta_query, engine, logger):

    logger.info('was xml 메타 만들기 시작')

    try:

        was_rtde_meta_group_df = pd.read_sql_query(
            was_group_meta_query, con=engine)
        was_rtde_meta_pgm_df = pd.read_sql_query(
            was_program_meta_query, con=engine)

        with open(was_xml_path+'rtde_was_meta.xml', 'w', encoding='utf-8') as file:
            file.write(XML_TYPE)
            file.write("<rtde>")

            # 프로그램그룹태그 생성
            process_group_data = reduce(process_group_row, was_rtde_meta_group_df.iterrows(), [])
            reduce(write_group_tag, process_group_data, file)

            # 프로그램태그 만들기
            process_program_data = reduce(process_group_row, was_rtde_meta_pgm_df.iterrows(), [])
            reduce(write_program_tag, process_program_data, file)

            file.write("</rtde>")
    except Exception as e:
        logger.exception(e)

    logger.info('was xml 메타 만들기 종료')


# lia xml 만들기
def make_lia_xml(lia_xml_path: str, lia_program_query: str, engine: sa.engine, logger: logging.Logger, args: argparse.Namespace):
    logger.info('lia 소스 xml 만들기 시작')

    try:

        lia_rtde_id_df = pd.read_sql_query(lia_program_query, con=engine)

        for idx in range(len(lia_rtde_id_df)):
            # pgm_grp_id별로 xml구성요소 읽기
            file_name = str(tuple(lia_rtde_id_df.values[idx])[0])+'.xml'
            logger.debug(file_name+'%s', '생성...')

            # XML헤더/풋터
            XML_TYPE = """<?xml version="1.0" encoding="UTF-8"?>\n"""
            xml_header = """<lia>\n"""
            xml_footer = "\n</lia>"

            s = str(DecryptFile.decrypt(lia_rtde_id_df['pgm_src'][idx]))
            s = trans(s, args)
            lia_rtde_id_df.loc[idx, 'pgm_src'] = make_cdata(
                s.strip('\n').strip('\r'))
            # XML파일생성
            with open(lia_xml_path+file_name, 'w', encoding='utf-8') as file:
                file.write(XML_TYPE)
                file.write(xml_header)
                file.write(lia_rtde_id_df['pgm_src'][idx])
                file.write(xml_footer)
    except Exception as e:
        logger.exception(e)

    logger.info('lia 소스 xml 만들기 종료')

    return len(lia_rtde_id_df)


# lia meta xml 만들기
def make_lia_meta_xml(lia_xml_path, lia_group_meta_query, lia_program_meta_query, engine, logger):

    logger.info('lia xml 메타 만들기 시작')

    try:
        lia_rtde_meta_group_df = pd.read_sql_query(
            lia_group_meta_query, con=engine)
        lia_rtde_meta_pgm_df = pd.read_sql_query(
            lia_program_meta_query, con=engine)

        with open(lia_xml_path+'rtde_lia_meta.xml', 'w', encoding='utf-8') as file:
            file.write(XML_TYPE)
            file.write("<rtde>")
            # 그룹태그 만들기
            for idx in range(len(lia_rtde_meta_group_df)):
                lia_rtde_meta_group_df.loc[idx, 'pgm_grp_desc'] = make_cdata(
                    str(DecryptFile.decrypt(lia_rtde_meta_group_df['pgm_grp_desc'][idx])))
                rows = tuple(lia_rtde_meta_group_df.values[idx])
                file.write("""<rtde_grp """)
                file.write("pgm_grp_id=\""+rows[0].replace('\\', '/')+"\" ")
                file.write("pgm_grp_nm=\""+rows[1]+"\" ")
                file.write("lia_type_cd=\""+rows[3]+"\" ")
                file.write("exec_ord_no=\""+str(math.trunc(rows[4]))+"\" ")
                file.write("reanly_exec_yn=\""+rows[5]+"\" ")
                file.write("exec_cond_yn=\""+rows[6]+"\" ")
                file.write("exec_pgm_id=\"" +
                           convNoneToEmptyString(rows[7])+"\" ")
                file.write("del_yn=\""+rows[8]+"\" ")
                file.write(""" >"""+euc2utf(rows[2])+'</rtde_grp>\n')

            # 프로그램태그 만들기
            for idx in range(len(lia_rtde_meta_pgm_df)):
                lia_rtde_meta_pgm_df.loc[idx, 'pgm_desc'] = make_cdata(
                    str(DecryptFile.decrypt(lia_rtde_meta_pgm_df['pgm_desc'][idx])))
                rows = tuple(lia_rtde_meta_pgm_df.values[idx])
                file.write("""<rtde_pgm """)
                file.write("pgm_id=\""+rows[0]+"\" ")
                file.write("pgm_grp_id=\""+rows[1].replace('\\', '/')+"\" ")
                file.write("lia_type_cd=\""+rows[2]+"\" ")
                file.write("db_type_cd=\""+rows[3]+"\" ")
                file.write("pgm_nm=\""+rows[4]+"\" ")
                file.write("exec_ord_no=\""+str(math.trunc(rows[5]))+"\" ")
                file.write("src_type_cd=\""+rows[6]+"\" ")
                file.write("sql_type_cd=\"" +
                           convNoneToEmptyString(rows[7])+"\" ")
                file.write("data_maker=\""+rows[9]+"\" ")
                file.write("common_exec_yn=\"" +
                           convNoneToEmptyString(rows[10])+"\" ")
                file.write("use_type_cd=\""+rows[11]+"\" ")
                file.write("del_yn=\""+rows[12]+"\" ")
                file.write(""" >"""+euc2utf(rows[8])+'</rtde_pgm>\n')
            file.write("</rtde>")
    except Exception as e:
        logger.exception(e)

    logger.info('lia xml 메타 만들기 종료')


def summary(logger, was_xml_count, lia_xml_count):
    logger.info('='*30)
    logger.info("""was xml 개수:%d""", was_xml_count)
    logger.info("""lia xml 개수:%d""", lia_xml_count)
    logger.info('='*30)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--db_url", '-db', help="for connect db", type=str)
    parser.add_argument("--schema_name", '-schema',
                        help="for change schema name", type=str)
    parser.add_argument("--transform_db", '-trans',
                        help="from postgresql to transform db", type=str)

    args = parser.parse_args()

    try:
        logger = set_log('./logging.yaml', 'db2xml')
        engine = create_engine(args)
        was_xml_path = set_xmldir('was', args.transform_db)
        lia_xml_path = set_xmldir('lia', args.transform_db)
        was_rtde_group_sql, was_rtde_id_sql = rtde_program_query(
            type='was', ais8800_table_name='ais8800', ais8801_table_name='ais8801')
        was_rtde_meta_group_sql = rtde_group_meta_query(
            type='was', ais8801_table_name='ais8801')
        was_rtde_meta_pgm_sql = rtde_program_meta_query(
            type='was', ais8800_table_name='ais8800')
        lia_rtde_id_sql = rtde_program_query(
            type='lia', ais8800_table_name='ais8800', ais8801_table_name='ais8801')
        lia_rtde_meta_group_sql = rtde_group_meta_query(
            type='lia', ais8801_table_name='ais8801')
        lia_rtde_meta_pgm_sql = rtde_program_meta_query(
            type='lia', ais8800_table_name='ais8800')

        start = time.time()

        if logger.isEnabledFor(level=10) is not True:
            max = os.cpu_count()
            print('max_workers:', max)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max) as e:
                was_xml_count = e.submit(
                    make_was_xml, was_xml_path, was_rtde_group_sql, was_rtde_id_sql, engine, logger, args)
                e.submit(make_was_meta_xml, was_xml_path,
                         was_rtde_meta_group_sql, was_rtde_meta_pgm_sql, engine, logger)
                lia_xml_count = e.submit(
                    make_lia_xml, lia_xml_path, lia_rtde_id_sql, engine, logger, args)
                e.submit(make_lia_meta_xml, lia_xml_path,
                         lia_rtde_meta_group_sql, lia_rtde_meta_pgm_sql, engine, logger)
            summary(logger, was_xml_count.result(), lia_xml_count.result())

        else:
            was_xml_count = make_was_xml(
                was_xml_path, was_rtde_group_sql, was_rtde_id_sql, engine, logger, args)
            make_was_meta_xml(was_xml_path, was_rtde_meta_group_sql,
                              was_rtde_meta_pgm_sql, engine, logger)
            lia_xml_count = make_lia_xml(
                lia_xml_path, lia_rtde_id_sql, engine, logger, args)
            make_lia_meta_xml(lia_xml_path, lia_rtde_meta_group_sql,
                              lia_rtde_meta_pgm_sql, engine, logger)
            summary(logger, was_xml_count, lia_xml_count)

        end = time.time()
        print(f'수행시간(초):{end - start}')

    except Exception as e:
        logger.error(e)
