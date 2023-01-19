#-*-coding:utf-8-*-
# informatica powercenter용 xml을 파싱하는 코드
import os
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

parsing_file = os.path.abspath("D:\\git\\python-edu\\xml\\RC_L0BIM_DBT_BLITEM_VOIP_GRP_01_C.xml")
with open(parsing_file,mode='r',encoding='utf-8') as f:
    xml = f.read()

## 아래 파서 구성
## REPOSITORY - FOLDER로 구성되어 있다.

attr_name = Regex('[a-zA-Z0-9_.-]+')
attr_value = QuotedString("'") | QuotedString('"')
attribute = attr_name + "=" + attr_value
attributes = ZeroOrMore(attribute)

# XML_DECLARE = Forward() # AST구문 클래스 임시정의 
# DOC_TYPE = Forward() # AST구문 클래스 임시정의
# POWERMART = Forward() # AST구문 클래스 임시정의
# REPOSITORY = Forward() # AST구문 클래스 임시정의
# FOLDER = Forward() # AST구문 클래스 임시정의
# SOURCE = Forward() # AST구문 클래스 임시정의
# TARGET = Forward() # AST구문 클래스 임시정의
# MAPPING = Forward() # AST구문 클래스 임시정의
# SHORTCUT = Forward() # AST구문 클래스 임시정의
# CONFIG = Forward() # AST구문 클래스 임시정의
# SESSION = Forward() # AST구문 클래스 임시정의
# WORKFLOW = Forward() # AST구문 클래스 임시정의
# CONNECTOR = Forward() # AST구문 클래스 임시정의
# SOURCEFIELD = Forward() # AST구문 클래스 임시정의
# TARGETFIELD = Forward() # AST구문 클래스 임시정의



SOURCEFIELD = OneOrMore("<SOURCEFIELD" + attributes + "/>")
TARGETFIELD = OneOrMore("<TARGETFIELD" + attributes + "/>")

SOURCE = "<SOURCE" + attributes + ">"+ Group(OneOrMore(SOURCEFIELD))+ "</SOURCE>" 
TARGET = "<TARGET" + attributes + ">"+ Group(OneOrMore(TARGETFIELD))+ "</TARGET>" 
MAPPING = "<MAPPING" + attributes + ">" + ... + "</MAPPING>" 
SHORTCUT ="<SHORTCUT" + attributes + ... + "/>" 
CONFIG = "<CONFIG" + attributes + ">" + ... + "</CONFIG>" 
SESSION = "<SESSION" + attributes + ">" + ... + "</SESSION>" 
WORKFLOW = "<WORKFLOW" + attributes + ">" + ... + "</WORKFLOW>" 

DOC_TYPE = "<!DOCTYPE"+Literal("POWERMART")+Literal("SYSTEM")+attr_value+">"

XML_DECLARE = "<?xml"+attributes+"?>"

SOURCE_FOLDER = "<FOLDER"+attributes+  ">" + SOURCE +"</FOLDER>"
TARGET_FOLDER = "<FOLDER"+attributes+  ">" + TARGET +"</FOLDER>"
MAPPING_FOLDER = "<FOLDER"+attributes+  ">" + (MAPPING & OneOrMore(SHORTCUT) & Suppress(CONFIG) & Suppress(SESSION) & Suppress(WORKFLOW)) +"</FOLDER>"

REPOSITORY = "<REPOSITORY"+attributes+  ">"+(TARGET_FOLDER & SOURCE_FOLDER & MAPPING_FOLDER)  +"</REPOSITORY>"

POWERMART = "<POWERMART" + attributes + ">" + REPOSITORY + "</POWERMART>" 

POWERMART.ignore(XML_DECLARE)
POWERMART.ignore(DOC_TYPE)

result = POWERMART.parse_file(parsing_file)

print(result.asDict())





