from bs4 import BeautifulSoup
import os
from datetime import datetime
import sqlalchemy as sa
import socket
from rtde.security import DecryptFile
from rtde.util import return_print,set_xmldir,set_log,create_engine
import logging,logging.config
import time
import concurrent.futures
import argparse

# 상수선언
WAS_META_XML = 'rtde_was_meta.xml'
LIA_META_XML = 'rtde_lia_meta.xml'
# 날짜
END_DT = '99991231235959'

def save_was_rtde_db(path_was_xml:str,was_meta_xml:str,engine:sa.engine,logger:logging.Logger,ais8801_table_name:str,ais8800_table_name:str):
    if ais8801_table_name is None:
        ais8801_table_name = 'ais8801'

    if ais8800_table_name is None:
        ais8800_table_name = 'ais8800'

    try:
        # was xml 목록
        was_xml_list = os.listdir(path_was_xml)
        was_xml_list.remove(was_meta_xml)

        # # was meta DB 저장
        data_file = open(path_was_xml+was_meta_xml,'r', encoding='utf-8')
        soup = BeautifulSoup(data_file,'xml')

        sql_insert_group = f'insert into {ais8801_table_name} values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        sql_update_group = f'update {ais8801_table_name} set pgm_grp_id = %s, aval_ed_dt = %s, aval_st_dt = %s where pgm_grp_id = %s and aval_ed_dt = %s'

        tag = soup.find_all('rtde_grp')
        was_meta_group_count = len(tag)
        with engine.connect() as conn:
            for e in tag :
                cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                alt_cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pgm_grp_id  = e.get('pgm_grp_id')
                pgm_grp_nm  = e.get('pgm_grp_nm')
                pgm_grp_desc= str(DecryptFile.encrypt(e.getText().strip('\n')))
                lia_type_cd = e.get('lia_type_cd')
                exec_ord_no = e.get('exec_ord_no')
                reanly_exec_yn= e.get('reanly_exec_yn')
                exec_cond_yn = e.get('exec_cond_yn')
                exec_pgm_id = e.get('exec_pgm_id')
                mdfy_user   = 'xml2db'
                ip_addr     = socket.gethostbyname(socket.gethostname())
                del_yn      = e.get('del_yn')
                conn.execute(sql_update_group,(pgm_grp_id,cur_dt,END_DT,pgm_grp_id,END_DT))
                conn.execute(sql_insert_group,(pgm_grp_id,END_DT,cur_dt,pgm_grp_nm,pgm_grp_desc,lia_type_cd,exec_ord_no,reanly_exec_yn,exec_cond_yn,exec_pgm_id,alt_cur_dt,mdfy_user,ip_addr,del_yn))
                logger.debug(pgm_grp_id)
        logger.info('was meta group 저장완료...')

        sql_insert_program = f'insert into {ais8800_table_name} values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        sql_update_program = f'update {ais8800_table_name} set pgm_id = %s , aval_ed_dt = %s , aval_st_dt = %s where pgm_id = %s and aval_ed_dt = %s'

        tag = soup.find_all('rtde_pgm')
        was_meta_program_count = len(tag)
        with engine.connect() as conn:
            for e in tag :
                cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                alt_cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pgm_id  = e.get('pgm_id')
                pgm_grp_id  = e.get('pgm_grp_id')
                lia_type_cd = e.get('lia_type_cd')
                db_type_cd  = e.get('db_type_cd')
                pgm_nm      = e.get('pgm_nm')
                exec_ord_no = e.get('exec_ord_no')
                pgm_src     = 'empty'
                src_type_cd = e.get('src_type_cd')
                sql_type_cd = e.get('sql_type_cd')
                pgm_desc    = str(DecryptFile.encrypt(e.getText().strip('\n')))
                data_maker  = e.get('data_maker')
                common_exec_yn= e.get('common_exec_yn')
                use_type_cd = e.get('use_type_cd')
                del_yn      = e.get('del_yn')
                mdfy_user   = 'xml2db'
                ip_addr     = socket.gethostbyname(socket.gethostname())

                conn.execute(sql_update_program,(pgm_id,cur_dt,END_DT,pgm_id,END_DT))
                conn.execute(sql_insert_program,(pgm_id,pgm_grp_id,END_DT,cur_dt,lia_type_cd,db_type_cd,pgm_nm,exec_ord_no,pgm_src,src_type_cd,sql_type_cd,pgm_desc,data_maker,common_exec_yn,use_type_cd,del_yn,alt_cur_dt,mdfy_user,ip_addr))
                logger.debug(pgm_id)
        logger.info('was meta program 저장완료...')

        # was pgm_src 저장
        with engine.connect() as conn:
            for was_xml in was_xml_list :
                data_file = open(path_was_xml+was_xml,'r', encoding='utf-8')
                soup = BeautifulSoup(data_file,'xml')

                sql_update_pgm_src = f'update {ais8800_table_name} set pgm_src = %s where pgm_id = %s and aval_ed_dt = %s'
                
                mybatis_xml_tag = ['resultMap','sql','select','insert','update','delete']
                for xml_tag in mybatis_xml_tag :
                    tag = soup.find_all(xml_tag)
                    for e in tag :
                        cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                        pgm_id = was_xml+'.'+ e.get('id')
                        pgm_src = str(DecryptFile.encrypt(return_print(e)))
                        conn.execute(sql_update_pgm_src,(pgm_src,pgm_id,END_DT))
                        logger.debug(pgm_id)
            logger.info('was program src 저장완료...')
    except Exception as e:
        logger.exception(e)
    finally:
        data_file.close()

    return (was_meta_group_count,was_meta_program_count)

def save_lia_rtde_db(path_lia_xml:str,lia_meta_xml:str,engine:sa.engine,logger:logging.Logger,ais8801_table_name:str,ais8800_table_name:str):
    
    if ais8801_table_name is None:
        ais8801_table_name = 'ais8801'

    if ais8800_table_name is None:
        ais8800_table_name = 'ais8800'

    try:
        # lia xml 목록
        lia_xml_list = os.listdir(path_lia_xml)
        lia_xml_list.remove(LIA_META_XML)

        # lia meta DB 저장
        data_file = open(path_lia_xml+LIA_META_XML,'r', encoding='utf-8')
        soup = BeautifulSoup(data_file,'xml')

        sql_insert_group = f'insert into {ais8801_table_name} values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        sql_update_group = f'update {ais8801_table_name} set pgm_grp_id = %s, aval_ed_dt = %s, aval_st_dt = %s where pgm_grp_id = %s and aval_ed_dt = %s'

        tag = soup.find_all('rtde_grp')
        lia_meta_group_count = len(tag)
        with engine.connect() as conn:
            for e in tag :
                cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                alt_cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pgm_grp_id  = e.get('pgm_grp_id')
                pgm_grp_nm  = e.get('pgm_grp_nm')
                pgm_grp_desc= str(DecryptFile.encrypt(e.getText().strip('\n')))
                lia_type_cd = e.get('lia_type_cd')
                exec_ord_no = e.get('exec_ord_no')
                reanly_exec_yn= e.get('reanly_exec_yn')
                exec_cond_yn = e.get('exec_cond_yn')
                exec_pgm_id = e.get('exec_pgm_id')
                mdfy_user   = 'xml2db'
                ip_addr     = socket.gethostbyname(socket.gethostname())
                del_yn      = e.get('del_yn')
                conn.execute(sql_update_group,(pgm_grp_id,cur_dt,END_DT,pgm_grp_id,END_DT))
                conn.execute(sql_insert_group,(pgm_grp_id,END_DT,cur_dt,pgm_grp_nm,pgm_grp_desc,lia_type_cd,exec_ord_no,reanly_exec_yn,exec_cond_yn,exec_pgm_id,alt_cur_dt,mdfy_user,ip_addr,del_yn))
                logger.debug(pgm_grp_id)
            logger.info('lia meta group 저장완료...')

        sql_insert_program = f'insert into {ais8800_table_name} values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        sql_update_program = f'update {ais8800_table_name} set pgm_id = %s , aval_ed_dt = %s , aval_st_dt = %s where pgm_id = %s and aval_ed_dt = %s'

        tag = soup.find_all('rtde_pgm')
        lia_meta_program_count = len(tag)
        with engine.connect() as conn:
            for e in tag :
                cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                alt_cur_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pgm_id  = e.get('pgm_id')
                pgm_grp_id  = e.get('pgm_grp_id')
                lia_type_cd = e.get('lia_type_cd')
                db_type_cd  = e.get('db_type_cd')
                pgm_nm      = e.get('pgm_nm')
                exec_ord_no = e.get('exec_ord_no')
                pgm_src     = 'empty'
                src_type_cd = e.get('src_type_cd')
                sql_type_cd = e.get('sql_type_cd')
                pgm_desc    = str(DecryptFile.encrypt(e.getText().strip('\n')))
                data_maker  = e.get('data_maker')
                common_exec_yn= e.get('common_exec_yn')
                use_type_cd = e.get('use_type_cd')
                del_yn      = e.get('del_yn')
                mdfy_user   = 'xml2db'
                ip_addr     = socket.gethostbyname(socket.gethostname())

                conn.execute(sql_update_program,(pgm_id,cur_dt,END_DT,pgm_id,END_DT))
                conn.execute(sql_insert_program,(pgm_id,pgm_grp_id,END_DT,cur_dt,lia_type_cd,db_type_cd,pgm_nm,exec_ord_no,pgm_src,src_type_cd,sql_type_cd,pgm_desc,data_maker,common_exec_yn,use_type_cd,del_yn,alt_cur_dt,mdfy_user,ip_addr))
                logger.debug(pgm_id)
            logger.info('lia meta program 저장완료...')

        # lia pgm_src 저장
        with engine.connect() as conn:
            for lia_xml in lia_xml_list :
                data_file = open(path_lia_xml+lia_xml,'r', encoding='utf-8')
                soup = BeautifulSoup(data_file,'xml')

                sql_update_pgm_src = f'update {ais8800_table_name} set pgm_src = %s where pgm_id = %s and aval_ed_dt = %s'
                
                mybatis_xml_tag = ['lia']
                for xml_tag in mybatis_xml_tag :
                    tag = soup.find_all(xml_tag)
                    for e in tag :
                        cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
                        pgm_id = lia_xml.rstrip("xml").rstrip('.')
                        pgm_src = str(DecryptFile.encrypt(e.getText().strip('\n')))
                        conn.execute(sql_update_pgm_src,(pgm_src,pgm_id,END_DT))
                        logger.debug(pgm_id)
            logger.info('lia program src 저장완료...')
    except Exception as e:
        logger.exception(e)
    finally:
        data_file.close()

    return (lia_meta_group_count, lia_meta_program_count)


def summary(logger,was_count,lia_count):
    logger.info('='*30)
    logger.info('was rtde 그룹 개수: %d',was_count[0])
    logger.info('was rtde 프로그램 개수: %d',was_count[1])
    logger.info('lia rtde 그룹 개수: %d',lia_count[0])
    logger.info('lia rtde 프로그램 개수: %d',lia_count[1])
    logger.info('='*30)

if __name__ == "__main__":
    
    parser=argparse.ArgumentParser()

    parser.add_argument("--db_url",'-db', help="for connect db",type=str)
    parser.add_argument("--transform_db",'-trans', help="from postgresql to transform db",type=str)

    args=parser.parse_args()
    
    try:
        logger =set_log('./logging.yaml','xml2db')
        engine = create_engine(args)
        was_xml_path = set_xmldir('was',args.transform_db) 
        lia_xml_path = set_xmldir('lia',args.transform_db)

        start = time.time()
        
        if logger.isEnabledFor(level=10) is not True:
            max = os.cpu_count()
            print('max_workers:',max)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max) as e:
                was_count = e.submit(save_was_rtde_db,was_xml_path,WAS_META_XML,engine,logger,'ais8801','ais8800')
                lia_count = e.submit(save_lia_rtde_db,lia_xml_path,LIA_META_XML,engine,logger,'ais8801','ais8800')
            summary(logger,was_count.result(),lia_count.result())

        else:
            was_count = save_was_rtde_db(was_xml_path,WAS_META_XML,engine,logger,'ais8801','ais8800')
            lia_count = save_lia_rtde_db(lia_xml_path,LIA_META_XML,engine,logger,'ais8801','ais8800')
            summary(logger,was_count,lia_count)

        end = time.time()
        print(f'수행시간(초):{end - start}')

    except Exception as e:
        logger.error(e)
