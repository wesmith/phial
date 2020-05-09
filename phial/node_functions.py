# Execute doctests using:
#   python3 node_functions.py  # reports nothing unless found errors
# For verbose output:
#   python3 node_functions.py 
"""Mechanisms (node-functions) for nodes.  
Allows for non-binary state nodes.
Each accepts the state from each of its immediately upstream nodes. 
It is an error to return a value that is not a state appropriate for
the node using the func.  
e.g. if NodeA.num_states==3, NodeA should not be assigned a func that
can ever return an int > 2.
The inputstates collection of can have 0 to N integers.
Functions should NOT ASSUME a specific number of values in inputstates.  
"""
from functools import reduce
import operator
import sys, inspect

# TODO:
#  decorator that adds attribute to func indicating how many inputs it handles
#  decorator that adds attribute to func indicating how many states it can return

def AND_func(inputstates):
    """Logical AND"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    #invals = [v != 0 for v in inputstates]
    return int(reduce(operator.and_, inputstates))

# In published papers, COPY seems to assume exactly one in-edge
def COPY_func(inputstates):
    """Copy single input"""
    assert len(inputstates) <= 1, (
        f"COPY_func must have 0,1 inputs. Got {len(inputstates)}" )
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return int(reduce(operator.or_, inputstates))

def MA_func(inputstates):
    """Mean Activation as state. Upto 15"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return min(15, int(sum(inputstates)/len(inputstates)))
COPY_func = MA_func #  Indended to have exactly one input node. 

def MAZ_func(inputstates):
    """Mean Activation gt zero"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return int((sum(inputstates)/len(inputstates)) > 0)

def MIN_func(inputstates):
    """Minimum state of inputstates"""
    return min(inputstates)

def MJ_func(inputstates):
    """Majority of inputs are non-zero"""
    return int(len([v for v in inputstates if v > 0]) > len(inputstates)/2)
MAJORITY_func=MJ_func

def MN_func(inputstates):
    """Minority of inputs are non-zero"""
    return int(len([v for v in inputstates if v > 0]) <= len(inputstates)/2)
MINORITY_func=MN_func

def NAND_func(inputstates):
    """Logical Not-AND"""
    return int(AND_func(inputstates) == 0)

def NOOP_func(inputstates):
    """Ignore inputstates"""
    return 0 # must return some state and we know there is at least one

def NOR_func(inputstates):
    """Logical Not-OR"""
    return int(OR_func(inputstates) == 0)

def NOT_func(inputstates):
    """Invert single input"""
    assert len(inputstates) <= 1, (
        f"NOT_func must have 0,1 inputs. Got {len(inputstates)}" )
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return int(inputstates[0] == 0)

def OR_func(inputstates):
    """Logical OR"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    #invals = [v != 0 for v in inputstates]
    return int(reduce(operator.or_, inputstates))

def PARITY_func(inputstates):
    """1 if sum of inputstates is odd"""
    return sum(inputstates) % 2

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

    
def XOR_func(inputstates):
    """Logical XOR. Odd number of inputs is true.
    >>> XOR_func([0,0])
    0
    >>> XOR_func([1,1])
    0
    >>> XOR_func([1,0])
    1
    >>> XOR_func([1,0,0])
    1
    >>> XOR_func([1,1,0])
    0
    >>> XOR_func([1,1,1])
    1
    """
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    nonzerovals = [v for v in inputstates if v > 0]
    return int(len(nonzerovals)%2 == 1)


##############################################################################

# Map func_name to executable function
funcLUT = dict(
    (name.replace('_func',''),obj)
    for name,obj in inspect.getmembers(sys.modules[__name__])
    if (inspect.isfunction(obj) and name.endswith('_func')))
# above allows:
# nf.funcLUT['AND'](inputs)  => 1


# Sorted list of all the node func names in this file.
node_functions = sorted(funcLUT.keys())
# above allows:
# import phial.node_functions as nf
# func_names = nf.node_functions

if __name__ == "__main__":
    import doctest
    doctest.testmod()

    
