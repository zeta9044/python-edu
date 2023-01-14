#디렉토리내. *.java, *.jj,*.jjt 파일리스트와 리스트 인코딩내용 보여주기
#파일을 UTF-8로 인코딩해서 저장하기

import os
import chardet
from pathlib import Path

def get_extension_list(dir:str,extension:str) -> list :
    copy_dir = dir
    copy_extension = extension
    return_list = list()
    for (root,dirs,files) in os.walk(copy_dir):
        row = [os.path.join(root,file) for file in files if file.endswith(copy_extension)] 
        if row != []:
            return_list = return_list + row
    return return_list

import chardet

def predict_encoding(file_path: Path, n_lines: int=20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
        encode_s = chardet.detect(rawdata)['encoding'].lower()
        if encode_s == 'euc-kr':
            encode_s = 'cp949'
    return encode_s

def get_encode_dic(file_list):
    encode_list = list()
    for e in file_list:
        encode_s = predict_encoding(e,200)
        if encode_s != 'utf-8':
            encode_list.append((e, encode_s))
    return dict(encode_list)

def convert_utf8(lang_list):
    jj = get_encode_dic(lang_list)
    for j in jj:
        try:
            if jj[j] != 'none' and jj[j] != 'utf-8':
                with open(j,"r",encoding=jj[j]) as read_file:
                    s = read_file.read()
                with open(j,"w",encoding='utf-8') as write_file:
                    write_file.write(s)
                print(f'before:{jj[j]},after:{predict_encoding(j,200)},file:{j}')
        except Exception as e:
            print(e)


if __name__ == "__main__":
    path = "d:\\git\\lia-engine"
    convert_utf8(get_extension_list(path,'.java'))
    convert_utf8(get_extension_list(path,'.groovy'))
    convert_utf8(get_extension_list(path,'.jj'))
    convert_utf8(get_extension_list(path,'.jjt'))

from tkinter import *

tk = Tk()
label = Label(tk,text='zeta')
label.pack()

def event():
    button['text'] = '버튼 누름'

button = Button(tk,text='버튼1,누르면 변해',command=event)
button.pack()
tk.mainloop()