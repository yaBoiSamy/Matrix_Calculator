import numpy as np


def to_float_if_1x1_ndarray(operand):  # if a value is a numpy array with scalar dimensions, convert it to float
    if isinstance(operand, np.ndarray) and operand.shape in {(1,), (1, 1)}:
        if operand.ndim == 1:
            operand = operand[0]
        elif operand.ndim == 2:
            operand = operand[0, 0]
    return operand


def to_vector_if_nx1_matrix(operand):  # if a matrix has the dimensions of a vector, convert it to a vector
    if isinstance(operand, np.ndarray) and operand.ndim == 2:
        if operand.shape[0] == 1:
            operand = operand[0, :]
        elif operand.shape[1] == 1:
            operand = operand[:, 0]
    return operand


def compute_addition(operand1, operand2):  # computes and manages errors for the '+' operator
    if isinstance(operand1, np.ndarray) and isinstance(operand2, np.ndarray) and operand1.shape != operand2.shape:
        raise ValueError(f"Addition not defined for matrices of shape {operand1.shape} and {operand2.shape}")
    return operand1 + operand2


def compute_hadamard_product(operand1, operand2):  # computes and manages errors for the '*' operator
    if isinstance(operand1, np.ndarray) and isinstance(operand2, np.ndarray) and operand1.shape != operand2.shape:
        raise ValueError(f"Hadamard product not defined for matrices of shape {operand1.shape} and {operand2.shape}")
    return operand1 * operand2


def compute_hadamard_division(operand1, operand2):  # computes and manages errors for the '/' operator
    if isinstance(operand1, float) and isinstance(operand2, np.ndarray):
        raise ValueError(f"Hadamard division not defined for scalar numerators accompanied by matrix denominators")
    if operand2 == 0 or isinstance(operand2, np.ndarray) and 0 in operand2:
        raise ZeroDivisionError("Division denominator contains or is equal to Zero")
    if isinstance(operand1, np.ndarray) and isinstance(operand2, np.ndarray) and operand1.shape != operand2.shape:
        raise ValueError(f"Hadamard division not defined for matrices of shape {operand1.shape} and {operand2.shape}")
    return operand1 / operand2


def compute_dot(operand1, operand2):  # computes and manages errors for the '@' operator
    if isinstance(operand1, float) or isinstance(operand2, float):
        return compute_hadamard_product(operand1, operand2)
    try:
        return to_float_if_1x1_ndarray(to_vector_if_nx1_matrix(operand1@operand2))
    except ValueError:
        raise ValueError(f"Dot product not defined for matrices of shape {operand1.shape} and {operand2.shape}")


def compute_exponent(base, exponent):  # computes and manages errors for the '^' operator
    if isinstance(exponent, np.ndarray):
        raise ValueError("This calculator does not support exponentiation by matrices yet. Sorry :/")
    if isinstance(base, float):
        return np.pow(base, exponent)
    if exponent % 1 != 0:
        raise ValueError("Matrix exponentiation is only defined for integer exponents")
    if base.ndim == 1 or base.shape[0] != base.shape[1]:
        raise ValueError("Matrix exponentiation is only defined for square matrix bases")
    try:
        return np.linalg.matrix_power(base, int(exponent))
    except np.linalg.LinAlgError:
        raise ValueError("Singular matrix, cannot be inverted")
