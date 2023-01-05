import pandas as pd
from datetime import datetime
import psycopg2
import os
from rtde.security import DecryptFile

print('시작')
        
def conv_nan_to_empty(input):
    if pd.isna(input):
        return ' '
    else:
        return input

    

conn = psycopg2.connect(host='192.168.0.160', dbname='postgres',user='LIAUSR',password='LIAUSR',port=5432)
cursor = conn.cursor()

excel_list = ['ImpactStreamInclude','ImpactStreamCommon','ImpactStreamInfo','ImpactStreamRelation','ImpactStreamFileDb','ImpactStreamHistory']

array_index = 0
for excel in excel_list :
    # 날짜
    cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
    end_dt = '99991231235959'
    
    #excel file load
    excel_group     = pd.read_excel((os.path.expanduser('~')+'\\downloads').replace('\\','/')+'/RTDE_'+excel_list[array_index]+'.xlsx',sheet_name='쿼리그룹')
    excel_program   = pd.read_excel((os.path.expanduser('~')+'\\downloads').replace('\\','/')+'/RTDE_'+excel_list[array_index]+'.xlsx',sheet_name='쿼리')

    sql_insert_group = 'insert into ais8801 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    sql_update_group = 'update ais8801 set pgm_grp_id = %s, aval_ed_dt = %s, aval_st_dt = %s where pgm_grp_id = %s and aval_ed_dt = %s'
    for idx in range(len(excel_group)) :
        #이력만들기
        id = excel_group['프로그램그룹ID'][idx]
        print((id,cur_dt,end_dt,id,end_dt))
        cursor.execute(sql_update_group,(id,cur_dt,end_dt,id,end_dt))
        #입력처리
        excel_group.loc[idx,'프로그램그룹설명'] = str(DecryptFile.encrypt(conv_nan_to_empty(excel_group['프로그램그룹설명'][idx])))
        excel_group.loc[idx,'실행순번'] = str(excel_group['실행순번'][idx])
        excel_group.loc[idx,'실행조건SQLID'] = str(excel_group['실행조건SQLID'][idx])
        cursor.execute(sql_insert_group, tuple(excel_group.values[idx]))
    conn.commit()

    sql_insert_program = 'insert into ais8800 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    sql_update_program = 'update ais8800 set pgm_id = %s , aval_ed_dt = %s , aval_st_dt = %s where pgm_id = %s and aval_ed_dt = %s'
    for idx in range(len(excel_program)) :
        #이력만들기
        id = excel_program['프로그램ID'][idx]
        print((id,cur_dt,end_dt,id,end_dt))
        cursor.execute(sql_update_program,(id,cur_dt,end_dt,id,end_dt))
        #입력처리
        excel_program.loc[idx,'소스내용'] = str(DecryptFile.encrypt(excel_program['소스내용'][idx]))
        excel_program.loc[idx,'프로그램설명'] = str(DecryptFile.encrypt(conv_nan_to_empty(excel_program['프로그램설명'][idx])))
        excel_program.loc[idx,'프로그램실행순번'] = str(excel_program['프로그램실행순번'][idx])
        excel_program.loc[idx,'데이터생성구분'] = str(excel_program['데이터생성구분'][idx])
        cursor.execute(sql_insert_program, tuple(excel_program.values[idx]))
    conn.commit()
    array_index = array_index + 1   

conn.close()

print('종료')

