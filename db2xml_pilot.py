import pandas as pd
from datetime import datetime
import psycopg2
import jpype
import os
import sqlalchemy as sa
import xml.etree.ElementTree as ET
import math
import chardet

# NoneType to Empty String function
def convNoneToEmptyString(o) :
    if o is None :
        o = ""
    return o

# UTF-8을 EUC-KR로 변환
def utf2euc(c):
    o = chardet.detect(c.encode())
    if o["encoding"] == 'UTF-8' :
        return str(c.encode(), 'utf-8').encode('euc-kr')
    else :
        return c
 
# EUC-KR을 UTF-8로 변환
def euc2utf(c):
    o = chardet.detect(c.encode())
    if o["encoding"] == 'EUC-KR' :
        s = str(c.encode(),'euc-kr').encode('utf-8')    
        #특수문자변환
        s.replace("<","&lt;").replace(">","&gt;").replace("&","&amp;").replace("\"","&quot;").replace("\'","&apos;")
        return s    
    else :
        return c.replace("<","&lt;").replace(">","&gt;").replace("&","&amp;").replace("\"","&quot;").replace("\'","&apos;")

#상수선언
PATH_WAS_XML = os.path.expanduser('~')+'/downloads/was_xml/'
os.makedirs(PATH_WAS_XML,exist_ok=True)
PATH_LIA_XML = os.path.expanduser('~')+'/downloads/lia_xml/'
os.makedirs(PATH_LIA_XML,exist_ok=True)

classpath = os.getcwd()+'/java-lib/lia-ds-cosec.jar'

#현재 경로에, java classpath 세팅
jpype.startJVM(jpype.getDefaultJVMPath(),"-Djava.class.path={classpath}".format(classpath=classpath),convertStrings=True)

#패키지 선언
jpkg = jpype.JPackage('com.lia.security')

#사용할 class선언 static일때는 () 붙이지 않는다.
DecryptFile = jpkg.DecryptFile

# DB접속
postgresql_url = 'postgresql://LIAUSR:LIAUSR@192.168.0.160:5432/postgres'
postgresql_conn = sa.create_engine(postgresql_url)

print('was 소스 xml 시작')
was_rtde_group_sql = """select
                            pgm_grp_id,
                            pgm_grp_nm
                        from
                            ais8801
                        where
                            lia_type_cd = '0'
                            and aval_ed_dt = '99991231235959'
                        order by pgm_grp_id,exec_ord_no""" 
was_rtde_id_sql = """select
                        A.PGM_ID,
                        A.PGM_GRP_ID,
                        B.PGM_GRP_NM,
                        B.EXEC_ORD_NO,
                        A.PGM_SRC
                    from
                        AIS8800 A,
                        AIS8801 B
                    where
                        A.AVAL_ED_DT = '99991231235959'
                        and A.LIA_TYPE_CD = '0'
                        and B.AVAL_ED_DT = '99991231235959'
                        and B.LIA_TYPE_CD = '0'
                        and A.PGM_GRP_ID = B.PGM_GRP_ID
                        and A.PGM_GRP_ID = %s
                        and B.PGM_GRP_NM= %s
                    order by
                        B.EXEC_ORD_NO,
                        A.PGM_GRP_ID,
                        A.EXEC_ORD_NO"""      

was_rtde_group_df = pd.read_sql_query(was_rtde_group_sql,con=postgresql_conn)

for idx in range(len(was_rtde_group_df)) :
    # pgm_grp_id별로 xml구성요소 읽기
    was_rtde_id_df = pd.read_sql_query(was_rtde_id_sql,con=postgresql_conn,params=tuple(was_rtde_group_df.values[idx]))
    temp_list = str(tuple(was_rtde_group_df.values[idx])[0]).replace('\\','/').split('/')
    file_name = temp_list[len(temp_list)-1]
    print(file_name,'생성...')

    # XML헤더/풋터 
    XML_TYPE = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    xml_header = """<mapper namespace="%s" >""" % tuple(was_rtde_group_df.values[idx])[1]
    xml_footer = "</mapper>" 
     
    # XML파일생성 
    with open(PATH_WAS_XML+file_name, 'w',encoding='utf-8') as file:
        file.write(xml_header)
        for inner_idx in range(len(was_rtde_id_df)) :
            was_rtde_id_df.loc[inner_idx,'pgm_src'] = str(DecryptFile.decrypt(was_rtde_id_df['pgm_src'][inner_idx]))
            file.write(was_rtde_id_df['pgm_src'][inner_idx])
        file.write(xml_footer)
    
    # XML파일 beautify
    with open(PATH_WAS_XML+file_name, 'r',encoding='utf-8') as file:
        element = ET.XML(file.read())
        ET.indent(element)
    with open(PATH_WAS_XML+file_name, 'w',encoding='utf-8') as file:
        file.write(XML_TYPE)
        file.write(ET.tostring(element,encoding='unicode'))
    
print('was 소스 xml 종료')

print('was 메타 xml 시작')
was_rtde_meta_group_sql = """select
                        pgm_grp_id
                        ,pgm_grp_nm
                        ,pgm_grp_desc
                        ,lia_type_cd
                        ,exec_ord_no
                        ,reanly_exec_yn
                        ,exec_cond_yn
                        ,exec_pgm_id
                        ,del_yn
                        from
                            ais8801
                        where
                            lia_type_cd = '0'
                            and aval_ed_dt = '99991231235959'
                        order by pgm_grp_id,exec_ord_no""" 
was_rtde_meta_pgm_sql = """select
                        pgm_id
                        ,pgm_grp_id
                        ,lia_type_cd
                        ,db_type_cd
                        ,pgm_nm
                        ,exec_ord_no
                        ,src_type_cd
                        ,sql_type_cd
                        ,pgm_desc
                        ,data_maker
                        ,common_exec_yn
                        ,use_type_cd
                        ,del_yn
                        from
                            ais8800
                        where
                            lia_type_cd = '0'
                            and aval_ed_dt = '99991231235959'
                        order by pgm_grp_id,exec_ord_no"""                             

was_rtde_meta_group_df = pd.read_sql_query(was_rtde_meta_group_sql,con=postgresql_conn)
was_rtde_meta_pgm_df = pd.read_sql_query(was_rtde_meta_pgm_sql,con=postgresql_conn)

with open(PATH_WAS_XML+'rtde_was_meta.xml','w',encoding='utf-8') as file :
    file.write(XML_TYPE)
    file.write("<rtde>")
    #그룹태그 만들기
    for idx in range(len(was_rtde_meta_group_df)) :
        was_rtde_meta_group_df.loc[idx,'pgm_grp_desc'] = str(DecryptFile.decrypt(was_rtde_meta_group_df['pgm_grp_desc'][idx]))
        rows = tuple(was_rtde_meta_group_df.values[idx])
        file.write("""<rtde_grp """)
        file.write("pgm_grp_id=\""+rows[0].replace('\\','/')+"\" ")
        file.write("pgm_grp_nm=\""+rows[1]+"\" ")
        file.write("lia_type_cd=\""+rows[3]+"\" ")
        file.write("exec_ord_no=\""+str(math.trunc(rows[4]))+"\" ")
        file.write("reanly_exec_yn=\""+rows[5]+"\" ")
        file.write("exec_cond_yn=\""+rows[6]+"\" ")
        file.write("exec_pgm_id=\""+convNoneToEmptyString(rows[7])+"\" ")
        file.write("del_yn=\""+rows[8]+"\" ")
        file.write(""" >"""+rows[2]+'</rtde_grp>\n')

    #프로그램태그 만들기
    for idx in range(len(was_rtde_meta_pgm_df)) :
        was_rtde_meta_pgm_df.loc[idx,'pgm_desc'] = str(DecryptFile.decrypt(was_rtde_meta_pgm_df['pgm_desc'][idx]))
        rows = tuple(was_rtde_meta_pgm_df.values[idx])
        file.write("""<rtde_pgm """)
        file.write("pgm_id=\""+rows[0]+"\" ")
        file.write("pgm_grp_id=\""+rows[1].replace('\\','/')+"\" ")
        file.write("lia_type_cd=\""+rows[2]+"\" ")
        file.write("db_type_cd=\""+rows[3]+"\" ")
        file.write("pgm_nm=\""+rows[4]+"\" ")
        file.write("exec_ord_no=\""+str(math.trunc(rows[5]))+"\" ")
        file.write("src_type_cd=\""+rows[6]+"\" ")
        file.write("sql_type_cd=\""+rows[7]+"\" ")
        file.write("data_maker=\""+str(math.trunc(rows[9]))+"\" ")
        file.write("common_exec_yn=\""+convNoneToEmptyString(rows[10])+"\" ")
        file.write("use_type_cd=\""+rows[11]+"\" ")
        file.write("del_yn=\""+rows[12]+"\" ")
        file.write(""" >"""+rows[8]+'</rtde_pgm>\n')        
    file.write("</rtde>")
print('was 메타 xml 종료')

print('lia 소스 xml 시작')
lia_rtde_id_sql = """select
                        A.PGM_ID,
                        A.PGM_GRP_ID,
                        A.EXEC_ORD_NO,
                        A.PGM_SRC
                    from
                        AIS8800 A
                    where
                        A.AVAL_ED_DT = '99991231235959'
                        and A.LIA_TYPE_CD != '0'
                    order by
                        A.PGM_GRP_ID,
                        A.EXEC_ORD_NO"""      

lia_rtde_id_df = pd.read_sql_query(lia_rtde_id_sql,con=postgresql_conn)

for idx in range(len(lia_rtde_id_df)) :
    # pgm_grp_id별로 xml구성요소 읽기
    file_name = str(tuple(lia_rtde_id_df.values[idx])[0])+'.xml'
    print(file_name,'생성...')

    # XML헤더/풋터 
    XML_TYPE = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    xml_header = """<lia>\n"""
    xml_footer = "\n</lia>" 
    
    lia_rtde_id_df.loc[idx,'pgm_src'] = str(DecryptFile.decrypt(lia_rtde_id_df['pgm_src'][idx]))
        # XML파일생성 
    with open(PATH_LIA_XML+file_name, 'w',encoding='utf-8') as file:
        file.write(XML_TYPE)
        file.write(xml_header)
        file.write(euc2utf(lia_rtde_id_df['pgm_src'][idx]))
        file.write(xml_footer)
print('lia 소스 xml 종료')

print('lia 메타 xml 시작')
lia_rtde_meta_group_sql = """select
                        pgm_grp_id
                        ,pgm_grp_nm
                        ,pgm_grp_desc
                        ,lia_type_cd
                        ,exec_ord_no
                        ,reanly_exec_yn
                        ,exec_cond_yn
                        ,exec_pgm_id
                        ,del_yn
                        from
                            ais8801
                        where
                            lia_type_cd != '0'
                            and aval_ed_dt = '99991231235959'
                        order by pgm_grp_id,exec_ord_no""" 
lia_rtde_meta_pgm_sql = """select
                        pgm_id
                        ,pgm_grp_id
                        ,lia_type_cd
                        ,db_type_cd
                        ,pgm_nm
                        ,exec_ord_no
                        ,src_type_cd
                        ,sql_type_cd
                        ,pgm_desc
                        ,data_maker
                        ,common_exec_yn
                        ,use_type_cd
                        ,del_yn
                        from
                            ais8800
                        where
                            lia_type_cd != '0'
                            and aval_ed_dt = '99991231235959'
                        order by pgm_grp_id,exec_ord_no"""                             

lia_rtde_meta_group_df = pd.read_sql_query(lia_rtde_meta_group_sql,con=postgresql_conn)
lia_rtde_meta_pgm_df = pd.read_sql_query(lia_rtde_meta_pgm_sql,con=postgresql_conn)

with open(PATH_LIA_XML+'rtde_lia_meta.xml','w',encoding='utf-8') as file :
    file.write(XML_TYPE)
    file.write("<rtde>")
    #그룹태그 만들기
    for idx in range(len(lia_rtde_meta_group_df)) :
        lia_rtde_meta_group_df.loc[idx,'pgm_grp_desc'] = str(DecryptFile.decrypt(lia_rtde_meta_group_df['pgm_grp_desc'][idx]))
        rows = tuple(lia_rtde_meta_group_df.values[idx])
        file.write("""<rtde_grp """)
        file.write("pgm_grp_id=\""+rows[0].replace('\\','/')+"\" ")
        file.write("pgm_grp_nm=\""+rows[1]+"\" ")
        file.write("lia_type_cd=\""+rows[3]+"\" ")
        file.write("exec_ord_no=\""+str(math.trunc(rows[4]))+"\" ")
        file.write("reanly_exec_yn=\""+rows[5]+"\" ")
        file.write("exec_cond_yn=\""+rows[6]+"\" ")
        file.write("exec_pgm_id=\""+convNoneToEmptyString(rows[7])+"\" ")
        file.write("del_yn=\""+rows[8]+"\" ")
        file.write(""" >"""+euc2utf(rows[2])+'</rtde_grp>\n')

    #프로그램태그 만들기
    for idx in range(len(lia_rtde_meta_pgm_df)) :
        lia_rtde_meta_pgm_df.loc[idx,'pgm_desc'] = str(DecryptFile.decrypt(lia_rtde_meta_pgm_df['pgm_desc'][idx]))
        rows = tuple(lia_rtde_meta_pgm_df.values[idx])
        file.write("""<rtde_pgm """)
        file.write("pgm_id=\""+rows[0]+"\" ")
        file.write("pgm_grp_id=\""+rows[1].replace('\\','/')+"\" ")
        file.write("lia_type_cd=\""+rows[2]+"\" ")
        file.write("db_type_cd=\""+rows[3]+"\" ")
        file.write("pgm_nm=\""+rows[4]+"\" ")
        file.write("exec_ord_no=\""+str(math.trunc(rows[5]))+"\" ")
        file.write("src_type_cd=\""+rows[6]+"\" ")
        file.write("sql_type_cd=\""+convNoneToEmptyString(rows[7])+"\" ")
        file.write("data_maker=\""+str(math.trunc(rows[9]))+"\" ")
        file.write("common_exec_yn=\""+convNoneToEmptyString(rows[10])+"\" ")
        file.write("use_type_cd=\""+rows[11]+"\" ")
        file.write("del_yn=\""+rows[12]+"\" ")
        file.write(""" >"""+euc2utf(rows[8])+'</rtde_pgm>\n')    
    file.write("</rtde>")       
print('lia 메타 xml 종료')
print('=============================')
print("""was xml 개수:""",len(was_rtde_group_df))
print("""lia xml 개수:""",len(lia_rtde_id_df))
print('=============================')