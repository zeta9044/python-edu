import jpype
import os
import sys

classpath = os.getcwd()+'/rtde/java-lib/lia-ds-cosec.jar'

#현재 경로에, java classpath 세팅
jpype.startJVM(jpype.getDefaultJVMPath(),"-Djava.class.path={classpath}".format(classpath=classpath),convertStrings=True)

#패키지 선언
jpkg = jpype.JPackage('com.lia.security')

#사용할 class선언 static일때는 () 붙이지 않는다.
DecryptFile = jpkg.DecryptFile

if __name__ == "__main__" :
    args = sys.argv[1:]

    def notice() :
        print("사용법: python security.py 암호화옵션 문자열")
        print("암호화옵션: e는 암호화, d는 복호화")

    if len(args) == 0 :
        notice()
    elif len(args) > 2 :
        notice()
    else :
        if args[0] == 'e' :
            if len(args[1]) > 0 :
                print(DecryptFile.encrypt(args[1]))
            else :
                print("암호화할 문자열을 입력하시오.")
        elif args[0] == 'd' :
            if len(args[1]) > 0 :
                print(DecryptFile.decrypt(args[1]))
            else :
                print("복호화할 문자열을 입력하시오.")
        else :
            notice()