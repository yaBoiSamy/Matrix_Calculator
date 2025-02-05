guide = """
Basic knowledge:
    This calculator has a variable repository.
    You can make a new variable by using the '=' operator.
    The nametag you place left of the '=' operator will become the name for your variable. Whatever value you place on
    the right of the operator will be stored in the variable.
    Not all nametags are permitted. As a general rule, avoid using symbols other than '_'.


Commands:
    To use a command, respect the following format:
    >> 'command name' 'parameter 1' 'parameter 2' ... etc.
    Here are the commands at your disposition:

    display -> Displays the variables with nametags corresponding to the parameters provided.
               If given no parameters, will display all variables.

    remove -> Deletes the variables with nametags corresponding to the parameters provided.
              If given no parameters, will remove all variables (after confirmation).

    decimals -> Adjusts the amount of decimals displayed to the amount specified in its first parameter.

    clear -> Clears the console

    guide -> Displays the guide (You used it to get here!)


Operation handling:
    All computations respect priority of operations.
    Matrices and vectors are made using accolades.
    Vectors are made by listing components inside the accolades. Ex: {1, 2, 3}
    Matrices are made by listing vectors inside the accolades. Ex: {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}
    Each vector used to instantiate a matrix is treated like a row of said matrix.
    Apart from matrix instantiation, vectors can act as row vectors or column vectors depending on context. 
    Whatever creates a valid operation.
    1-component vectors and 1x1 matrices are treated like scalars, 
    Determinants are computed by wrapping an operation that yields a matrix inside of brackets. Ex: [{{1, 2}, {3, 4}}]
    IMPORTANT: Everything is recursive. You can use an operation as a component to an object you want to instantiate. 
    Ex: [{X@Y, {[Y]/3, 0}}] Is a valid operation (if X is a 2-component vector and Y is a 2x2 matrix)
    Here are the operators at your disposition:

    + -> used identically to traditional mathematics.
    - -> used identically to traditional mathematics.

    * -> Element-wise multiplication when used on two matrices, normal multiplication when scalars are involved.
    / -> Element-wise division when used on two matrices, normal division when scalars are involved.
    @ -> Dot product when used on Vectors and Matrices, normal multiplication when scalars are involved.

    ^ -> Used for exponentiation. When the exponent is negative, inverts the base before exponentiation.
         Used identically to traditional mathematics otherwise.


"""