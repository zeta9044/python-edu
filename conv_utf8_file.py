import chardet
import codecs
import os
import shutil

def convert_to_utf8(file_path):
    # 인코딩 타입 확인
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        print(f'{file_path} is encoded in {result["encoding"]}')
        f.seek(0) 

    # 파일명에 utf-8이 있다면 이름을 바꾸지 않고, 없다면 utf-8로 변경
    if 'utf-8' in result["encoding"]:
        return
    else:
        new_file_path = os.path.splitext(file_path)[0] + '_utf-8' + os.path.splitext(file_path)[1]

    # 인코딩 타입을 utf-8로 변환하여 새로운 파일로 저장
    with codecs.open(file_path, 'r', encoding=result["encoding"], errors='ignore') as f_input, codecs.open(new_file_path, 'w', encoding='utf-8') as f_output:
        f_output.write(f_input.read())

    # 기존파일에 덮어쓰기
    shutil.move(new_file_path,file_path)


convert_to_utf8('c:/Users/zeta/Downloads/cp949.txt')