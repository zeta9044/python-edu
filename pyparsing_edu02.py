from pyparsing import *

class Example3:
    def __init__(self):
        self.count = 0

    def MatchedBraces(self, input_string):
        lbrace = Literal("{")
        rbrace = Literal("}")
        matched_braces = Forward()
        matched_braces << (lbrace + Optional(matched_braces) + rbrace)
        matched_braces.set_parse_action(self.convert)
        return matched_braces.transform_string(input_string)


    def count_up(self, s, l, t):
        print("token:",t)
        self.count += 1

    def convert(self,s,l,t):
        copy_t = t
        print('token:',t)
        for index,item in enumerate(copy_t):
            if item=='{':
                copy_t[index]='['
            elif item=='}':
                copy_t[index]=']'
        print('return_token:',copy_t)
        return copy_t

    def Input(self, input_string):
        result = self.MatchedBraces(input_string)
        print(result)

example3 = Example3()
example3.Input("{ { { } } }")
