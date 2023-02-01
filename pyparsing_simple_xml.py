#-*-coding:utf-8-*-
# informatica powercenter용 xml을 파싱하는 코드
import os
import json
from pyparsing import *


parsing_file = os.path.abspath("D:\\git\\python-edu\\xml\\sample.xml")
with open(parsing_file,mode='r',encoding='utf-8') as f:
    xml = f.read()

## 아래 파서 구성
## REPOSITORY - FOLDER로 구성되어 있다.

attr_name = Regex('[a-zA-Z0-9_.-]+')
content = Regex('[a-zA-Z0-9_.-]+')
attr_value = QuotedString("'") | QuotedString('"')
attribute = attr_name + Suppress("=") + attr_value
attributes = ZeroOrMore(attribute)
content.set_parse_action(lambda s,l,t:print(t))
slash = Literal("/")
left_angle_bracket = Literal("<")
right_angle_bracket = Literal(">")
tag_name = Regex('[A-Z0-9_]+')
open_tag = left_angle_bracket+tag_name+attributes+right_angle_bracket
any_close_tag = slash+right_angle_bracket
close_tag = left_angle_bracket+slash+tag_name+right_angle_bracket
simple_tag = left_angle_bracket+tag_name+attributes+any_close_tag
tag = Forward()
tag <<= open_tag +Opt(Group(ZeroOrMore(content) & ZeroOrMore(tag) & ZeroOrMore(simple_tag))) + close_tag

xml_declare = "<?xml"+SkipTo("?>")+"?>"
doc_type= "<!DOCTYPE"+SkipTo(">")+">"

xml_expression = xml_declare + Opt(doc_type) + tag
# result=pp.set_debug(True).parse_file(parsing_file)

# xml_expression.setTraceParseAction(["name","args"])
# xml_expression.set_debug()
# print(pyparsing_test.with_line_numbers(xml))
# result = xml_expression.parse_string(xml)
result = xml_expression.parse_file(parsing_file)
# result.pprint()

print(type(result))
print(type(list(result)))

s=""
for i in result:
    if not isinstance(i,str):
        for x in i.items():
            print(x)
        # s=s+' '.join([x for x in i.values()])
    else:
        s=s+i
print("="*100)
print(s)