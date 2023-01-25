#-*-coding:utf-8-*-
# informatica powercenter용 xml을 파싱하는 코드
import os
import json
from pyparsing import (
    Word,
    alphas,
    ParseException,
    Literal,
    CaselessLiteral,
    CaselessKeyword,
    FollowedBy,
    Combine,
    Optional,
    nums,
    Forward,
    ZeroOrMore,
    StringEnd,
    alphanums,
    QuotedString,
    Suppress,
    SkipTo,
    make_xml_tags, Word, alphas, Suppress, Optional, delimitedList,Regex,
    make_html_tags, Word, alphas, QuotedString, ZeroOrMore, OneOrMore, pprint,one_of,Group
)

parsing_file = os.path.abspath("D:\\git\\python-edu\\xml\\sample.xml")
with open(parsing_file,mode='r',encoding='utf-8') as f:
    xml = f.read()


def sudo_code(s,l,tok):
    d = dict()
    try:
        tuple_list = list()
        temp_list = list()
        for index, item in enumerate(tok):
            if (index+1)%2 in (0,1):
                tuple_list.append(item)
                if len(tuple_list) == 2:
                    temp_list.append(tuple(tuple_list))
                    tuple_list.clear()
        d = dict(temp_list)
        d = {key:val for key,val in d.items() if key =='NAME'}
    except Exception as e:
        print(e)
    return d
## 아래 파서 구성
## REPOSITORY - FOLDER로 구성되어 있다.

attr_name = Regex('[a-zA-Z0-9_.-]+')
attr_value = QuotedString("'") | QuotedString('"')
attribute = attr_name + Suppress("=") + attr_value
attributes = ZeroOrMore(attribute)
attributes.set_parse_action(sudo_code)

SOURCEFIELD = (Suppress("<SOURCEFIELD") + attributes + Suppress("/>")).set_results_name("sourcefield")[1,...]  
TARGETFIELD = (Suppress("<TARGETFIELD") + attributes + Suppress("/>")).set_results_name("targetfield")[1,...]    

SOURCE = (Suppress("<SOURCE") + attributes + Suppress(">")+ Group(SOURCEFIELD)+ Suppress("</SOURCE>")).set_results_name("source") 
TARGET = (Suppress("<TARGET") + attributes + Suppress(">")+ Group(TARGETFIELD)+ Suppress("</TARGET>")).set_results_name("target")  
MAPPING = (Suppress("<MAPPING") + attributes + Suppress(">") + Suppress(SkipTo("</MAPPING>")) + Suppress("</MAPPING>")).set_results_name("mapping") 
SHORTCUT =(Suppress("<SHORTCUT") + attributes + Suppress("/>")).set_results_name("shortcut")[1,...]
CONFIG = Suppress("<CONFIG") + attributes + Suppress(">") + ... + Suppress("</CONFIG>") 
SESSION = Suppress("<SESSION") + attributes + Suppress(">") + ... + Suppress("</SESSION>") 
WORKFLOW = Suppress("<WORKFLOW") + attributes + Suppress(">") + ... + Suppress("</WORKFLOW>") 

DOC_TYPE = "<!DOCTYPE"+Literal("POWERMART")+Literal("SYSTEM")+attr_value+Suppress(">")

XML_DECLARE = "<?xml"+attributes+"?>"

SOURCE_FOLDER = (Suppress("<FOLDER")+attributes+  Suppress(">") + Group(SOURCE) +Suppress("</FOLDER>"))("source_folder")
TARGET_FOLDER = (Suppress("<FOLDER")+attributes+  Suppress(">") + Group(TARGET) +Suppress("</FOLDER>"))("target_folder")
MAPPING_FOLDER = (Suppress("<FOLDER")+attributes+  Suppress(">") + Group((MAPPING & SHORTCUT & Suppress(CONFIG) & Suppress(SESSION) & Suppress(WORKFLOW))) +Suppress("</FOLDER>"))("mapping_folder")
REPOSITORY = (Suppress("<REPOSITORY")+attributes+  Suppress(">")+ Group(TARGET_FOLDER & SOURCE_FOLDER & MAPPING_FOLDER)  +Suppress("</REPOSITORY>"))("repository")
POWERMART = (Suppress("<POWERMART") + attributes + Suppress(Literal(">")) + Group(REPOSITORY) + Suppress("</POWERMART>")).set_results_name("powermart")   
POWERMART.ignore(XML_DECLARE)
POWERMART.ignore(DOC_TYPE)

result = POWERMART.parse_file(parsing_file)

print(json.dumps(result.asDict(),indent=4))
