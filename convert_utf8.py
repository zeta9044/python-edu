# 디렉토리내. *.java, *.jj,*.jjt 파일리스트와 리스트 인코딩내용 보여주기
# 파일을 UTF-8로 인코딩해서 저장하기
from pathlib import Path
import chardet
import codecs
import os
import shutil
from functools import reduce

# extension별 파일리스트
def get_extension_list(dir: str, extension: str) -> list:
    copy_dir = dir
    copy_extension = extension
    return_list = list()
    for (root, dirs, files) in os.walk(copy_dir):
        row = [os.path.join(root, file)
               for file in files if file.endswith(copy_extension)]
        if row != []:
            return_list = return_list + row
    return return_list

# 인코딩 타입 
def predict_encoding(file_path: Path, n_lines: int = 20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])
        encode_s = chardet.detect(rawdata)['encoding'].lower()
        if encode_s == 'euc-kr':
            encode_s = 'cp949'
    return encode_s

# 인코딩 타입 
def get_encoding(file_path: Path):
    # 인코딩 타입 확인
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        val = result["encoding"].lower()
        process_type = 'cp949' if val== 'euc-kr' else val
        print(f'{file_path} is encoded in {val}')
        f.seek(0)
        return process_type

# 일급함수 활용. try/catch를 사용하는 함수로 변경
# 파이썬에서는 익명함수는 한줄짜리 lambda만 허용한다.
# lambda를 제외한 모든 함수는 명칭을 갖는다.
def wrap_try_catch(func):
    def try_catch(args):
        try:
            func(args)
        except Exception as e:
            print(e)
    return try_catch

# reduce를 사용하기 위해서, accumlator자리에 _를 넣었다.
# _는 아무값이나 와도 된다는 파이썬의 선언.
def convert_to_uft8_file(file_path: Path):
    # 인코딩 타입 확인
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        print(f'{file_path} is encoded in {result["encoding"]}')
        f.seek(0)

    # 파일명에 utf-8이 있다면 이름을 바꾸지 않고, 없다면 utf-8로 변경
    if 'utf-8' in result["encoding"]:
        return
    else:
        new_file_path = os.path.splitext(
            file_path)[0] + '_utf-8' + os.path.splitext(file_path)[1]

    # 인코딩 타입을 utf-8로 변환하여 새로운 파일로 저장
    with codecs.open(file_path, 'r', encoding=result["encoding"], errors='ignore') as f_input, codecs.open(new_file_path, 'w', encoding='utf-8') as f_output:
        f_output.write(f_input.read())

    # 기존파일에 덮어쓰기
    shutil.move(new_file_path, file_path)


def get_encode_dic(file_list):
    encode_list = list()
    for e in file_list:
        encode_s = predict_encoding(e, 200)
        if encode_s != 'utf-8':
            encode_list.append((e, encode_s))
    return dict(encode_list)


def convert_utf8(lang_list):
    jj = get_encode_dic(lang_list)
    for j in jj:
        try:
            if jj[j] != 'none' and jj[j] != 'utf-8':
                with open(j, "r", encoding=jj[j]) as read_file:
                    s = read_file.read()
                with open(j, "w", encoding='utf-8') as write_file:
                    write_file.write(s)
                print(
                    f'before:{jj[j]},after:{predict_encoding(j,200)},file:{j}')
        except Exception as e:
            print(e)

def convert_utf8_dir(dir_path:Path,file_extension:str) -> None:
    file_list = get_extension_list(dir_path,file_extension)
    print('total file count:',len(file_list))
    convert_to_uft8_file_with_try_catch = wrap_try_catch(convert_to_uft8_file)
    for file in file_list:
        convert_to_uft8_file_with_try_catch(file)

if __name__ == "__main__":
    path = "e:\\git\\lia-engine"
    convert_utf8(get_extension_list(path, '.java'))
    convert_utf8(get_extension_list(path, '.groovy'))
    convert_utf8(get_extension_list(path, '.jj'))
    convert_utf8(get_extension_list(path, '.jjt'))

    dir='c:/Users/zeta/Downloads'
    convert_utf8_dir(dir,'.txt')