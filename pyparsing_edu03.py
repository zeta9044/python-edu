from pyparsing import *

# Define a grammar for a simple Python program
integer = Word(nums)
plus = Literal("+")
expr = integer + plus + integer

# Define the transformation function
@expr.set_parse_action
def change_plus_to_minus(s,l,t):
    copy_t = t
    for index, item in enumerate(copy_t):
        if item=='+':
            copy_t[index]='-'
    return copy_t

# Parse the original source code
original_code = "1 + 2"
modified_code = expr.transformString(original_code)
print(modified_code)
