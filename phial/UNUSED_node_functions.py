# The are set aside for various reasons.
# Some are alias of funcs in node_functions.py
# Some are for non-binary nodes, which is not supported by phi-calc.


def MA_func(inputstates):
    """Mean Activation as state. Upto 15"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return min(15, int(sum(inputstates)/len(inputstates)))

def MAZ_func(inputstates):
    """Mean Activation gt zero"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return int((sum(inputstates)/len(inputstates)) > 0)

def MIN_func(inputstates):
    """Minimum state of inputstates"""
    return min(inputstates)

def TRI_func(inputstates):
    """Count input states. Produces 3 states"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    if sum(inputstates) == 0:
        return 0
    if sum(inputstates) == 1:
        return 1
    else:
        return 2

def PARITY_func(inputstates):
    """1 if sum of inputstates is odd"""
    return sum(inputstates) % 2
    
