from pyparsing import *

# Define the grammar
lbrace = Literal("{")
rbrace = Literal("}")

def MatchedBraces():
    return Forward()

matched_braces = MatchedBraces()
matched_braces << (lbrace + Optional(matched_braces) + rbrace)

def Input():
    return matched_braces + StringEnd()

# Create the parser
example2_parser = Input()

# Test the parser
test_string = "{ { } } "
result = example2_parser.parseString(test_string)
print(result)
