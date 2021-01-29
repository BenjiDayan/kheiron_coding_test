# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 17:25:58 2021

@author: benja
"""
import json
import re
from collections import deque
from operator import mul, add, truediv
minus = lambda a, b: a - b


"""
> 3                     # 3
3
> + 1 2                 # 1 + 2
3
> + 1 * 2 3             # 1 + (2 * 3)
7
> + * 1 2 3             # (1 * 2) + 3
5
> - / 10 + 1 1 * 1 2    # - / 10 (1 + 1) (1 * 2)
3
> - 0 3                 # (0 - 3)
-3
> / 3 2                 # (3 / 2)
1 (or 1.5)


operators bind to the right where possible. the whole expression is read from
right to left.
"""

operator_chars = {'+':add, '-':minus, '*':mul, '/':truediv}
brackets = ('(', ')')
replacements = {'(': '[', ')':']'}
for operator_char in operator_chars:
    replacements[operator_char] = f'"{operator_char}"'


def parse_line(my_str):
    """my_str: (str) e.g. '( 1 + ( 2 * 3 ) )'
    return: (list) [[1.0, '+', [2.0, '*', 3.0]]]
    """
    
    my_str = '( ' + my_str.strip() + ' )'
   
    # turn ints into floats
    my_str = re.sub(r"(\d) ", r"\1.0 ", my_str)
    
    # puts commas between non brackets
    my_str = re.sub('((?<![()])) ((?![()]))', r'\1,\2', my_str)
    my_str = re.sub('((?<![(])) ([(])', r'\1,\2', my_str)
    my_str = re.sub('([)]) ((?![)]))', r'\1,\2', my_str)
    my_str = re.sub('([)]) ([(])', r'\1,\2', my_str)
    
    # replace brackets with square brackets, enclose operators in double quotes
    for original_char, replacement_char in replacements.items():
        my_str = my_str.replace(original_char, replacement_char)
    
    split_list = json.loads(my_str)    
    
    return split_list

def compute_expression(my_str):
    split_list = parse_line(my_str)
    return evaluate_elt_list_with_recursion(split_list)    
    
def compute_expression_v2(my_str):
    split_list = parse_line(my_str)
    return evaluate_elt_list_with_queue_stack(split_list)    
    
    
def evaluate_elt_list_with_queue_stack(elt_list):
    """elt_list: (list) e.g.[['/', 6.0, 3.0], '-', 4.5]
    return: (float) -2.5
    
    I think a better implementation.
    """
    operator_queue = deque()
    num_stack = []
    for elt in reversed(elt_list):
        if isinstance(elt, list):
            elt = evaluate_elt_list_with_queue_stack(elt)
        if elt in operator_chars:
            operator_queue.append(elt)
        else:
            num_stack.append(elt)
        if len(operator_queue) > 0 and len(num_stack) >= 2:
            op = operator_chars[operator_queue.popleft()]
            a, b = num_stack[-1], num_stack[-2]
            num_stack[-2:] = [op(a, b)]
            
    if len(num_stack) != 1:
        raise Exception(f'remaining num_stack of length {len(num_stack)}')
    return num_stack[0]
    

def evaluate_elt_list_with_recursion(elt_list):
    """elt_list: (list) e.g.[['/', 6.0, 3.0], '-', 4.5]
    return: (float) -2.5
    
    Uses recursion, not a very good implementation"""
    
    # I think a doubly linked list implementation would be most efficient
    # in this recursion approach
    
    num_elts = len(elt_list)
    if num_elts == 1:
        if isinstance(elt_list[0], float):
            return elt_list[0]
        elif isinstance(elt_list[0], list):
            return evaluate_elt_list_with_recursion(elt_list[0])
        raise Exception(f'last remaining element is {elt_list[0]}')
        

    for i in range(num_elts - 1, -1, -1):
        elt = elt_list[i]
        if isinstance(elt, list):
            elt_list[i] = evaluate_elt_list_with_recursion(elt)
            elt = elt_list[i]
        if elt in operator_chars:
            if i > num_elts - 3:
                if num_elts - 3 >= 0:
                    val = evaluate_triple(elt_list[-3:])
                    new_list = elt_list[:num_elts - 3] + [val]
                    return evaluate_elt_list_with_recursion(new_list)
                    
            # Is this inefficient? All the list copying
            a, b = elt_list[i+1], elt_list[i+2]
            new_list = elt_list[:i] + [operator_chars[elt](a, b)] + elt_list[i+3:]
            return evaluate_elt_list_with_recursion(new_list)
            
    raise Exception(f'ran out of operators: remaining elt_list: {elt_list}')
    

def evaluate_triple(elts_triple):
    """a + b, + a b, a b + -> eval(a+b)
    elts_triple: e.g. [1.0, "+", 2.3]
    """
    floats, operators = [], []
    for elt in elts_triple:
        if isinstance(elt, list):
            elt = evaluate_elt_list_with_recursion(elt)
        if elt in operator_chars:
            operators.append(elt)
        else:
            floats.append(elt)

    if len(operators) != 1:
        raise Exception(f'Should be exactly one operator in elts_triple: {elts_triple}')
    
    return operator_chars[operators[0]](floats[0], floats[1])
        

tests = {'3': 3, '+ 1 2':3, '+ 1 * 2 3':7, '+ * 1 2 3':5, 
         '- / 10 + 1 1 * 1 2':3, '- 0 3':-3, '/ 3 2':1.5,
         '1 + 2':3, '* 2 2 + 3':10, '* 2 2 3 +':10,
         '( 1 + 2 )':3, '( 1 + ( 2 * 3 ) )':7, 
         '( ( 1 * 2 ) + 3 )':5, '( ( ( 1 + 1 ) / 10 ) - ( 1 * 2 ) )':-1.8}
def test_parse_line(compute_func):
    for my_str, val in tests.items():
        print(f'input: {my_str}, expected: {val}, got: {compute_func(my_str)}')
        assert compute_func(my_str) == val
        
        
if __name__ == '__main__':
    print('testing compute_expression')
    test_parse_line(compute_expression)
    print('\ntesting compute_expression_v2')
    test_parse_line(compute_expression_v2)
