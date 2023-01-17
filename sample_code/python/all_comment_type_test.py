#!/usr/bin/env python3
"""
Add two components, x and y do not have to be of the same type
param x: First parameter
param y: Second parameter
return: Return addition of x and y 'accordingly'
"""

def add(x,y):
    return x + y

print(add("he","llo"))
print(add("2","llo"))
# Prints documentation comments to terminal
print(__doc__)

str1 = """Hello"""
print(str1)

"""
Round-trip invariant for limited input:
        # Output text will tokenize the back to the input
        t1 = [tok[:2] for tok in generate_tokens(f.readline)]
        newcode = untokenize(t1)
        readline = iter(newcode.splitlines(1)).next
        t2 = [tok[:2] for tok in generate_tokens(readline)]
        assert t1 == t2
 t1 = [tok[:2] for tok in generate_tokens(f.readline)]
        newcode = untokenize(t1)
        readline = iter(newcode.splitlines(1)).next
        t2 = [tok[:2] for tok in generate_tokens(readline)]
        assert t1 == t2
"""

# Give arguments x and y
# x and y must be of the same type
# Return the difference between x and y
def subtract(x,y):
    return x - y


""" We can't Withdraw Money without it being in the bank 
Args:
    Money_withdrawn (float): The amount of Money Withdrawn 
    Total_money (float): Total Money in the account

Raises:
    RuntimeError: Amount Withdrawn greater than Total_Money

Returns:
    float: Remaining Money
"""