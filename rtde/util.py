import chardet
from io import StringIO
import yaml
import os
import sys
import argparse
import logging,logging.config
import sqlalchemy as sa

def getlogConf(file_name) :
    with open(file_name, 'r') as stream:
        try:
            parsed_yaml=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return parsed_yaml

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
        return s    
    else :
        return c
# xml에서 허용하지 않는 <=,>= 을 대체문자로 변경
def alt_char(c):
    return c.replace("<![CDATA[<>]]>","&lt;&gt;").replace("<![CDATA[<=]]>","&lt;=").replace("<![CDATA[>=]]>","&gt;=").replace("<![CDATA[<]]>","&lt;").replace("<![CDATA[>]]>","&gt;").replace("<=","&lt;=").replace(">=","&gt;=")

# print의 문자열반환 함수
def return_print(*message):
    io = StringIO()
    print(*message, file=io, end="")
    return io.getvalue()        


# xml 생성위치
def set_xmldir(type:str,to:str):
    try:
        if to is not None :
            path = '/downloads/'+to+'/'+type+'_xml/'
        else:
            if len(sys.argv) ==2:
                db_name=(sys.argv[1]).split(':')[0]
                if db_name == 'postgresql':
                    db_name == 'postgres'
            else:
                db_name='postgres'
            path = '/downloads/'+db_name+'/'+type+'_xml/'

        if type == 'was':
            xml_path = os.path.expanduser('~')+path
            os.makedirs(xml_path,exist_ok=True)
            return xml_path
        elif type == 'lia':
            xml_path = os.path.expanduser('~')+path
            os.makedirs(xml_path,exist_ok=True)
            return xml_path
        else :
            raise ValueError('type에는 was 또는 lia를 입력해야 합니다.')    
    except Exception as e:
        print(e)

# CDATA만들기 <![CDATA[]]>
def make_cdata(string:str):
    return "<![CDATA[\n"+string+"\n]]>"

# qtrack table 리스트 (table,view 포함)
def read_qtrack_table_list():
    with open("./qtrack_table_list.txt",mode='r') as file:
        list = [ x.strip().upper() for x in file]
    return list

# 문자열과 스키마명을 받아서, 문자열내 table명 앞에 스키마 붙이기
def attach_schema_name(s,shema_name,table_list):
    blank=" "
    comma=","
    cr="\n"
    for table in table_list:
        s=s.replace(comma+table+comma,comma+shema_name+table+comma)
        s=s.replace(blank+table+comma,blank+shema_name+table+comma)
        s=s.replace(comma+table+blank,comma+shema_name+table+blank)
        s=s.replace(blank+table+blank,blank+shema_name+table+blank)
        s=s.replace(blank+table+cr,blank+shema_name+table+cr)
        s=s.replace(comma+table+cr,comma+shema_name+table+cr)
        s=s.replace(cr+table+cr,cr+shema_name+table+cr)
    for table in table_list:
        table = table.lower()
        s=s.replace(comma+table+comma,comma+shema_name+table+comma)
        s=s.replace(blank+table+comma,blank+shema_name+table+comma)
        s=s.replace(comma+table+blank,comma+shema_name+table+blank)
        s=s.replace(blank+table+blank,blank+shema_name+table+blank)
        s=s.replace(blank+table+cr,blank+shema_name+table+cr)
        s=s.replace(comma+table+cr,comma+shema_name+table+cr)
        s=s.replace(cr+table+cr,cr+shema_name+table+cr)
    return s    

# postgres에서 oracle변환되는 매핑 딕셔너리
def get_transform_dic():
    with open('./transform_mapping.txt','r',encoding='utf-8') as file:
        L = eval(file.read().replace('\n',''))
    return dict(iter(L))

# 문자열과 변환사전을 받아서 postgresql을 oracle로 변경한 후 문자열 반환
def tranform_postgres_to_oracle(s,transform_dic:dict):
    for key in transform_dic:
        s = s.replace(key,transform_dic.get(key))
    return s    


# 로그설정
def set_log(yaml_location, logger_name):
    logging.config.dictConfig(getlogConf(yaml_location))
    logger = logging.getLogger(logger_name)
    return logger

# DB접속, 매개변수 받기 정의
def create_engine(args:argparse.Namespace):
    if args is None:
        db_url = 'postgresql://LIAUSR:LIAUSR@192.168.0.160:5432/postgres'
    else :
        db_url = args.db_url
    return sa.create_engine(db_url)    
