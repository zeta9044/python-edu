import pandas as pd
from datetime import datetime
import psycopg2
import os
from rtde.security import DecryptFile

print('시작')

def get_src(str):
    if str.startswith("D:\\LIA-Engine"):
        try:
            file = open(str,mode='r',encoding='utf-8')
            str = file.read()
            print(str)
            file.close()
        except FileNotFoundError:
            pass
    return str
        
def conv_nan_to_empty(input):
    if pd.isna(input):
        return ' '
    else:
        return input

    

conn = psycopg2.connect(host='192.168.0.160', dbname='postgres',user='LIAUSR',password='LIAUSR',port=5432)
cursor = conn.cursor()

rtde_excel_file = 'RTDE_ProgramList_postgreSQL'

# 날짜
cur_dt = datetime.now().strftime("%Y%m%d%H%M%S")
end_dt = '99991231235959'

#excel file load
excel_group     = pd.read_excel((os.path.expanduser('~')+'\\downloads').replace('\\','/')+'/'+rtde_excel_file+'.xlsx',sheet_name='쿼리그룹')
excel_program   = pd.read_excel((os.path.expanduser('~')+'\\downloads').replace('\\','/')+'/'+rtde_excel_file+'.xlsx',sheet_name='쿼리')

sql_insert_group = 'insert into ais8801 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
sql_update_group = 'update ais8801 set pgm_grp_id = %s, aval_ed_dt = %s, aval_st_dt = %s where pgm_grp_id = %s and aval_ed_dt = %s'
for idx in range(len(excel_group)) :
    #이력만들기
    id = excel_group['프로그램그룹ID'][idx]
    print((id,cur_dt,end_dt,id,end_dt))
    cursor.execute(sql_update_group,(id,cur_dt,end_dt,id,end_dt))
    #입력처리
    pgm_grp_id      = str(conv_nan_to_empty(excel_group['프로그램그룹ID'][idx]))
    aval_ed_dt      = end_dt
    aval_st_dt      = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    pgm_grp_nm      = str(conv_nan_to_empty(excel_group['프로그램그룹명'][idx]))
    pgm_grp_desc    = str(conv_nan_to_empty(DecryptFile.encrypt(conv_nan_to_empty(excel_group['프로그램그룹설명'][idx]))))
    lia_type_cd     = str(conv_nan_to_empty(excel_group['LIA유형코드'][idx]))
    exec_ord_no     = str(conv_nan_to_empty(excel_group['실행순번'][idx]))
    reanly_exec_yn  = str(conv_nan_to_empty(excel_group['재분석실행여부'][idx]))
    exec_cond_yn    = str(conv_nan_to_empty(excel_group['실행조건여부'][idx]))
    exec_pgm_id     = str(conv_nan_to_empty(excel_group['실행조건SQLID'][idx]))
    mdfy_date       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mdfy_user       = str(conv_nan_to_empty(excel_program['변경자'][idx]))
    print([pgm_grp_id,aval_ed_dt,aval_st_dt,pgm_grp_nm,pgm_grp_desc,lia_type_cd,exec_ord_no,reanly_exec_yn,exec_cond_yn,exec_pgm_id,mdfy_date,mdfy_user])
    cursor.execute(sql_insert_group,[pgm_grp_id,aval_ed_dt,aval_st_dt,pgm_grp_nm,pgm_grp_desc,lia_type_cd,exec_ord_no,reanly_exec_yn,exec_cond_yn,exec_pgm_id,mdfy_date,mdfy_user])
conn.commit()

sql_insert_program = 'insert into ais8800 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
sql_update_program = 'update ais8800 set pgm_id = %s , aval_ed_dt = %s , aval_st_dt = %s where pgm_id = %s and aval_ed_dt = %s'
for idx in range(len(excel_program)) :
    #이력만들기
    id = excel_program['프로그램ID'][idx]
    print((id,cur_dt,end_dt,id,end_dt))
    cursor.execute(sql_update_program,(id,cur_dt,end_dt,id,end_dt))
    #입력처리
    pgm_id          = str(conv_nan_to_empty(excel_program['프로그램ID'][idx]))
    pgm_grp_id      = str(conv_nan_to_empty(excel_program['프로그램그룹ID'][idx]))
    aval_ed_dt      = end_dt
    aval_st_dt      = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    lia_type_cd     = str(conv_nan_to_empty(excel_program['LIA유형코드'][idx]))
    db_type_cd      = str(conv_nan_to_empty(excel_program['DB유형코드'][idx]))
    pgm_nm          = str(conv_nan_to_empty(excel_program['프로그램명'][idx]))
    exec_ord_no     = str(conv_nan_to_empty(excel_program['프로그램실행순번'][idx]))
    pgm_src         = str(DecryptFile.encrypt(get_src(excel_program['소스내용'][idx]).replace("_x000D_","")))
    src_type_cd     = str(conv_nan_to_empty(excel_program['소스유형코드'][idx]))
    sql_type_cd     = str(conv_nan_to_empty(excel_program['SQL유형코드'][idx]))
    pgm_desc        = str(DecryptFile.encrypt(conv_nan_to_empty(excel_program['프로그램설명'][idx]).replace("_x000D_","")))
    data_maker      = str(conv_nan_to_empty(excel_program['데이터생성구분'][idx]))
    common_exec_yn  = str(conv_nan_to_empty(excel_program['공통실행여부'][idx]))
    use_type_cd     = str(conv_nan_to_empty(excel_program['사용유형코드'][idx]))
    del_yn          = str(conv_nan_to_empty(excel_program['삭제여부'][idx]))
    mdfy_date       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mdfy_user       = str(conv_nan_to_empty(excel_program['변경자'][idx]))
    print([pgm_id,pgm_grp_id,aval_ed_dt,aval_st_dt,lia_type_cd,db_type_cd,pgm_nm,exec_ord_no,DecryptFile.decrypt(pgm_src),src_type_cd,sql_type_cd,pgm_desc,data_maker,common_exec_yn,use_type_cd,del_yn,mdfy_date,mdfy_user])
    cursor.execute(sql_insert_program, [pgm_id,pgm_grp_id,aval_ed_dt,aval_st_dt,lia_type_cd,db_type_cd,pgm_nm,exec_ord_no,pgm_src,src_type_cd,sql_type_cd,pgm_desc,data_maker,common_exec_yn,use_type_cd,del_yn,mdfy_date,mdfy_user])
conn.commit()
conn.close()

print('종료')

