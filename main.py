import numpy as np
from ast import literal_eval

operand_chars = {' ', '+', '-', '*', '/', '@', '^', '=', '(', ')', '[', ']', '{', '}', ','}

parentheses_matchups = {
    '(': ')',
    '[': ']',
    '{': '}'
}

variable_repertoire = {}


def parse_input(string):  # Removes spaces and seperates input into manipulateable substrings
    parsed_arr = [""]
    for c in string:
        if c in operand_chars:
            if c != ' ':
                parsed_arr.append(c)
            parsed_arr.append("")
        else:
            parsed_arr[-1] += c
    return [subs for subs in parsed_arr if subs != ""]


class OperatorError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ShapeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ParenthesesError(Exception):
    def __init__(self, message):
        super().__init__(message)


def guard_clauses(parsed_input):
    subs_to_index = {}  # for constant-time operator lookup
    for i, subs in enumerate(parsed_input):
        if subs in subs_to_index:
            subs_to_index[subs].append(i)
        else:
            subs_to_index[subs] = [i]

    # Checking for equality signs assigning operations, not new martices
    if '=' in subs_to_index and tuple(subs_to_index['=']) not in {(0,), (1,)}:
        raise OperatorError("'=' operator misused.")

    # Checking for matrices without operators
    last_subs = parsed_input[0]
    for subs in parsed_input[1:]:
        if last_subs not in operand_chars and subs not in operand_chars:
            raise OperatorError(f"Matrices '{last_subs}' and '{subs}' not seperated by an operator")
        last_subs = subs

    # Checking for illegal contiguous operators
    incompatibilities = {
        '+': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '-': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '*': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '/': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '@': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '^': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '=': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '(': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        ')': {'='},
        '[': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        ']': {'@', '=', '(', ']', '{'},
        '{': {'*', '/', '@', '^', '=', ')', '[', ']', '}'},
        '}': {'/', '='},
        ',': {'*', '/', '@', '^', '=', ')', '[', ']', '}'}
    }
    last_subs = parsed_input[0]
    for subs in parsed_input[1:]:
        if last_subs in operand_chars and subs in incompatibilities[last_subs]:
            raise OperatorError(f"'{last_subs}' and '{subs}' cannot be used contiguously")
        last_subs = subs if subs not in {'-', '+'} else last_subs

    # Looking for parentheses issues
    stack = []
    for subs in parsed_input:
        if subs in {'(', '[', '{'}:
            stack.append(subs)
        elif subs in {')', ']', '}'}:
            topOfStack = stack.pop()
            if subs != parentheses_matchups[topOfStack]:
                raise ParenthesesError(f"Could not find closing parentheses for '{topOfStack}'")


def parse_num_or_reference(subs):
    try:
        return float(subs)
    except ValueError:
        try:
            return variable_repertoire[subs]
        except KeyError:
            raise LookupError(f"Variable of name {subs} not found in repertoire.")


def apply_sub_operation(operation_contents, sub_operation_delimiter, sub_operation_process):
    sub_operation_coordinates = []
    depth = 0
    for i, subs in enumerate(operation_contents):
        if subs == sub_operation_delimiter:
            if depth == 0:
                sub_operation_coordinates.append(i)
            depth += 1
        elif subs == parentheses_matchups[sub_operation_delimiter]:
            depth -= 1
            if depth == 0:
                sub_operation_coordinates[-1] = (sub_operation_coordinates[-1], i + 1)
    processed_operation_contents = []
    last_exit_coordinate = 0
    for left_index, right_index in sub_operation_coordinates:
        processed_operation_contents += (operation_contents[last_exit_coordinate:left_index] +
                                    [sub_operation_process(operation_contents[left_index + 1:right_index - 1])])
        last_exit_coordinate = right_index
    processed_operation_contents += operation_contents[last_exit_coordinate:]
    return processed_operation_contents


def parse_operation(operation_contents):
    # Recursive Case
    operation_contents = apply_sub_operation(operation_contents, '(', parse_operation)

    # Convert every matrix to nd arrays
    operation_contents = apply_sub_operation(operation_contents, '{', parse_matrix)

    # Recursion base case ; compute the operations
    # TODO: complete the base case
    return operation_contents


def parse_matrix(matrix_contents):
    matrix_stack = []
    current_layer = matrix_stack
    buffer = []
    for subs in matrix_contents:
        if subs == '{':
            if current_layer != matrix_stack:
                raise ShapeError("This calculator does not support rank 3+ tensors. Sorry :/")
            matrix_stack.append([])
            current_layer = matrix_stack[-1]
        elif subs == '}':
            current_layer = matrix_stack
        elif subs == ',':
            element_contents = parse_operation(buffer)
            if current_layer != matrix_stack or element_contents.ndim not in {0, 1}:
                raise ShapeError("This calculator does not support rank 3+ tensors. Sorry :/")
            current_layer.append(element_contents)
        else:
            buffer.append(subs)
    try:
        return np.array(matrix_stack)
    except ValueError:
        raise ShapeError("Matrix contents are not of homogenous size.")


def main():
    parsed_input = parse_input(input())
    try:
        guard_clauses(parsed_input)
    except Exception as e:
        print(e)


while True:
    main()
