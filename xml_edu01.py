import pyparsing as pp

pp.ParserElement.enable_packrat()

NAME = pp.Regex(r"\w+\d+")
@NAME.set_parse_action
def translate(result: pp.ParseResults) -> str:
    return result

@NAME.add_parse_action
def add(s:str,loc:int,result: pp.ParseResults) -> str:
    return result  

print(NAME[...]("name*").set_debug(flag=True).parse_string("abc123 a213123123",parse_all=True))