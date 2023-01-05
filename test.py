from bs4 import BeautifulSoup
from openpyxl import Workbook
from datetime import datetime
import re
import os
from rtde.util import return_print,set_log,create_engine
import copy
import functools
    
write_wb = Workbook()
write_progam = write_wb.create_sheet("ddd",0)
write_progam['A1'] = "프로그램ID"
write_progam['B1'] = "프로그램그룹ID"
write_progam['C1'] = "유효종료일자"
write_progam['D1'] = "유효시작일자"
write_progam['E1'] = "LIA유형코드"
write_progam['F1'] = "DB유형코드"
write_progam['G1'] = "프로그램명"
write_progam['H1'] = "프로그램실행순번"
write_progam['I1'] = "소스내용"
write_progam['J1'] = "소스유형코드"
write_progam['K1'] = "SQL유형코드"
write_progam['L1'] = "프로그램설명"
write_progam['M1'] = "데이터생성구분"
write_progam['N1'] = "공통실행여부"
write_progam['O1'] = "사용유형코드"
write_progam['P1'] = "삭제여부"
write_progam['Q1'] = "변경일시"
write_progam['R1'] = "변경자"

