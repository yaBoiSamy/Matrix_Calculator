import numpy as np
import os
import Operations as ops
from Guide import guide

operator_chars = {' ', '+', '-', '*', '/', '@', '^', '=', '(', ')', '[', ']', '{', '}', ','}
parentheses_matchups = {'(': ')', '[': ']', '{': '}'}
variable_repertoire = {}
default_name_index = 0
decimals = 3


def isOperator(subs):  # Detects when an object is in the operator_chars set. Saves space in many if statements
    return isinstance(subs, str) and subs in operator_chars


def generate_default_name():  # generates default names when no nametag is specified left of the '=' operator
    global default_name_index
    name = f"m{default_name_index}"
    default_name_index += 1
    return name


def parse_num_or_reference(subs):  # turns substrings of numbers or variable names into their actual value
    try:
        return float(subs)
    except ValueError:
        try:
            return variable_repertoire[subs]
        except KeyError:
            raise LookupError(f"Variable of name '{subs}' not found in repertoire.")


def apply_sub_operation(operation_contents, sub_operation_delimiter, sub_operation_process):  # Applies parentheses-delimited operations to their respective section
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


def compute_determinant(operation_contents):  # Turns [ ... ] into a determinant
    matrix = parse_operation(operation_contents)
    if not (isinstance(matrix, np.ndarray) and matrix.ndim == 2):
        raise ValueError("Determinant is not defined for scalar values and vectors")
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Determinant is not defined for non-square matrices")
    return np.linalg.det(matrix)


def parse_matrix(matrix_contents):  # Turns { ... } into a matrix/vector
    def integrate_matrix_subsection():
        nonlocal buffer
        nonlocal current_layer
        if not buffer:
            return
        matrix_subsection = parse_operation(buffer)
        if isinstance(matrix_subsection, np.ndarray) and (current_layer != matrix_stack or matrix_subsection.ndim != 1):
            raise ValueError("This calculator does not support rank 3+ tensors. Sorry :/")
        current_layer.append(matrix_subsection)
        buffer = []

    matrix_stack = []
    current_layer = matrix_stack
    buffer = []
    for subs in matrix_contents:
        if subs == '{':
            if current_layer != matrix_stack:
                raise ValueError("This calculator does not support rank 3+ tensors. Sorry :/")
            matrix_stack.append([])
            current_layer = matrix_stack[-1]
        elif subs == '}':
            integrate_matrix_subsection()
            current_layer = matrix_stack
        elif subs == ',':
            integrate_matrix_subsection()
        else:
            buffer.append(subs)
    integrate_matrix_subsection()
    try:
        return ops.to_float_if_1x1_ndarray(ops.to_vector_if_nx1_matrix(np.array(matrix_stack)))
    except ValueError:
        raise ValueError("Matrix contents are not of homogenous size.")


def parse_operation(operation_contents):  # recursive function that takes care of operation order
    # --------------- Recursive Case ---------------
    operation_contents = apply_sub_operation(operation_contents, '(', parse_operation)
    operation_contents = apply_sub_operation(operation_contents, '[', compute_determinant)
    operation_contents = apply_sub_operation(operation_contents, '{', parse_matrix)

    # --------------- Base Case ---------------
    # convert all floats, variables and such to numbers/matrices
    for i, subs in enumerate(operation_contents):
        if not isinstance(subs, np.ndarray) and not isOperator(subs):
            operation_contents[i] = parse_num_or_reference(subs)

    # get rid of + signs, use - signs to multiply the following element by -1
    next_operation_contents = []
    flip_next = False
    for subs in operation_contents:
        if not isOperator(subs):
            next_operation_contents.append(subs * (-1 if flip_next else 1))
            flip_next = False
        elif subs == '+':
            continue
        elif subs == '-':
            flip_next = not flip_next
        else:  # for all the operators apart from '+' and '-'
            next_operation_contents.append(subs)
    operation_contents = next_operation_contents

    # compute all exponents
    next_operation_contents = []
    compute_at_next = False
    for subs in operation_contents:
        if isOperator(subs) and subs == '^':
            compute_at_next = True
        elif compute_at_next:
            next_operation_contents.append(ops.compute_exponent(next_operation_contents.pop(), subs))
            compute_at_next = False
        else:
            next_operation_contents.append(subs)
    operation_contents = next_operation_contents

    # compute all products
    next_operation_contents = []
    compute_at_next = None
    for subs in operation_contents:
        if isOperator(subs) and subs in {'*', '/', '@'}:
            compute_at_next = subs
        elif compute_at_next == '*':
            next_operation_contents.append(ops.compute_hadamard_product(next_operation_contents.pop(), subs))
            compute_at_next = None
        elif compute_at_next == '/':
            next_operation_contents.append(ops.compute_hadamard_division(next_operation_contents.pop(), subs))
            compute_at_next = None
        elif compute_at_next == '@':
            next_operation_contents.append(ops.compute_dot(next_operation_contents.pop(), subs))
            compute_at_next = None
        else:
            next_operation_contents.append(subs)
    operation_contents = next_operation_contents

    # sum up what's left
    next_operation_contents = operation_contents[0]
    for subs in operation_contents[1:]:
        next_operation_contents = ops.compute_addition(next_operation_contents, subs)
    operation_contents = next_operation_contents

    return operation_contents


def remove_variables(*args):  # removes all variable names given to it
    global variable_repertoire
    for nametag in args:
        if nametag in variable_repertoire:
            del variable_repertoire[nametag]
            print(f"Removed {nametag} successfully")
        else:
            print(f"Variable {nametag} was not found")
    print()


def display_variables(*args):  # displays all variables names given to it
    global variable_repertoire
    if not args:
        print("Repertoire empty, no variables to display\n")
        return
    for nametag in args:
        if nametag in variable_repertoire:
            print(f"{nametag}:\n{np.round(variable_repertoire[nametag], decimals)}\n")
        else:
            print(f"Variable {nametag} was not found\n")


def parse_input(string):  # Removes spaces and separates input into substrings delimited by operators
    parsed_arr = [""]
    for c in string:
        if c in operator_chars:
            if c != ' ':
                parsed_arr.append(c)
            parsed_arr.append("")
        else:
            parsed_arr[-1] += c
    return [subs for subs in parsed_arr if subs != ""]


def check_for_commands(parsed_input):
    global variable_repertoire
    global decimals
    
    # Returns True if a command was executed, otherwise false
    match (parsed_input[0]):
        case "remove":
            if not parsed_input[1:] and 'y' == input("Confirm deletion of all variables (y/n): "):
                variable_repertoire = {}
                return True
            remove_variables(*tuple(parsed_input[1:]))
            return True
        case "display":
            if not parsed_input[1:]:
                display_variables(*tuple(variable_repertoire.keys()))
                return True
            display_variables(*tuple(parsed_input[1:]))
            return True
        case "clear":
            if parsed_input[1:]:
                raise ValueError("Too many arguments for command 'clear'")
            os.system('cls')
            return True
        case "Guide":
            if parsed_input[1:]:
                raise ValueError("Too many arguments for command 'Guide'")
            print(guide)
            return True
        case "decimals":
            if not parsed_input[1:]:
                raise ValueError("Too few arguments for command 'decimals'")
            if len(parsed_input[1:]) > 1:
                raise ValueError("Too many arguments for command 'decimals'")
            try:
                float(parsed_input[1])
            except ValueError:
                raise ValueError(f"'{parsed_input[1]}' not an integer")
            if float(parsed_input[1]) % 1 != 0:
                raise ValueError("Decimal count must be an integer")
            decimals = int(parsed_input[1])
            return True
    return False


def guard_clauses(parsed_input):
    # Checking for equality signs assigning operations, not new matrices
    if '=' in parsed_input and parsed_input.index('=') not in {0, 1}:
        raise ValueError("'=' operator misused.")

    # Checking for matrices without operators
    last_subs = parsed_input[0]
    for subs in parsed_input[1:]:
        if not isOperator(last_subs) and not isOperator(subs):
            raise ValueError(f"Matrices '{last_subs}' and '{subs}' not separated by an operator")
        last_subs = subs

    # Checking for illegal contiguous operators
    incompatibilities = {
        '+': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '-': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '*': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '/': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '@': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '^': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '=': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '(': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        ')': {'=', '(', '[', '{'},
        '[': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        ']': {'=', '(', '[', '{'},
        '{': {'*', '/', '@', '^', '=', ')', ']', '}', ','},
        '}': {'=', '(', '[', '{'},
        ',': {'*', '/', '@', '^', '=', ')', ']', '}', ','}
    }
    last_subs = parsed_input[0]
    last_plusminus_subs = None
    for subs in parsed_input[1:]:
        if isOperator(last_subs) and subs in incompatibilities[last_subs]:
            raise ValueError(f"'{last_subs}' and '{subs}' cannot be used contiguously")
        if last_plusminus_subs is not None and subs in incompatibilities[last_plusminus_subs]:
            raise ValueError(f"'{last_plusminus_subs}' and '{subs}' cannot be used contiguously")
        if subs in {'+', '-'}:
            last_plusminus_subs = subs
        else:
            last_subs = subs
            last_plusminus_subs = None

    # Looking for parentheses issues
    stack = []
    for subs in parsed_input:
        if subs in {'(', '[', '{'}:
            stack.append(subs)
        elif subs in {')', ']', '}'}:
            if not stack:
                raise ValueError(f"Could not find opening parentheses for '{subs}'")
            topOfStack = stack.pop()
            if subs != parentheses_matchups[topOfStack]:
                raise ValueError(f"Could not find closing parentheses for '{topOfStack}'")
    if stack:
        raise ValueError(f"Could not find closing parentheses for '{stack[-1]}'")


def manage_operation(parsed_input):
    forbidden = {'.', '\'', '\"', '<', '>', '\\', '|', '/', '?', '!', '#', '$', '%', '&', '«', '»'} | operator_chars
    digits = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
    nametag = "Result"
    if len(parsed_input) >= 2 and parsed_input[0] == '=':
        nametag = generate_default_name()
        result = parse_operation(parsed_input[1:])
        variable_repertoire[nametag] = result
    elif len(parsed_input) >= 3 and parsed_input[1] == '=':
        nametag = parsed_input[0]
        if nametag[0] in digits:
            raise ValueError("Variable nametag cannot start with a digit")
        if set(nametag) & forbidden:
            raise ValueError(f"Variable nametag cannot contain characters {set(nametag) & forbidden}")
        result = parse_operation(parsed_input[2:])
        variable_repertoire[nametag] = result
    else:
        result = parse_operation(parsed_input)
    print(f"{nametag}:\n{np.round(result, decimals)}\n")


def main():
    parsed_input = parse_input(input(">> "))
    if not parsed_input:
        return
    try:
        if check_for_commands(parsed_input):
            return
        guard_clauses(parsed_input)
        manage_operation(parsed_input)
    except Exception as e:
        print(e)


print("To access command guide, type 'Guide' below")
while True:
    main()
