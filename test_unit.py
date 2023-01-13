#암호화 관련
from rtde.security import DecryptFile

s="""2aede8dd11d68f9d5384d712c88f58c9|29f29b8c6b841175564bd8eaee04e74e|7c14347e7fda0eaa4f904d7a57745b52"""

list = s.split('|')


t = tuple(map(DecryptFile.decrypt,list))
print(t)

# for e in m:
#     print(e)

