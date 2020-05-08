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

# TODO:
#  decorator that adds attribute to func indicating how many inputs it handles
#  decorator that adds attribute to func indicating how many states it can return

def noop_func(inputstates):
    """Ignore inputstates"""
    return 0 # must return some state and we know there is at least one

def ma_func(inputstates):
    """Mean Activation as state. Upto 15"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return min(15, int(sum(inputstates)/len(inputstates)))
copy_func = ma_func #  Indended to have exactly one input node. 

def maz_func(inputstates):
    """Mean Activation gt zero"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    return int((sum(inputstates)/len(inputstates)) > 0)

def tri_func(inputstates):
    """Count input states. Produces 3 states"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    if sum(inputstates) == 0:
        return 0
    if sum(inputstates) == 1:
        return 1
    else:
        return 2

def or_func(inputstates):
    """Logical OR"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in inputstates]
    return int(reduce(operator.or_, invals)    )

def nor_func(inputstates):
    """Logical Not-OR"""
    return int(or_func(inputstates) == 0)

# In published papers, COPY seems to assume exactly one in-edge
def copy_func(inputstates):
    """Copy single input"""
    assert len(inputstates) <= 1, (
        f"copy_func must have 0,1 inputs. Got {len(inputstates)}" )
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in inputstates]
    return int(reduce(operator.or_, invals))

def xor_func(inputstates):
    """Logical XOR"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in inputstates]
    return int(reduce(operator.xor, invals))

def and_func(inputstates):
    """Logical AND"""
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in inputstates]
    return int(reduce(operator.and_, invals))

def nand_func(inputstates):
    """Logical Not-AND"""
    return int(and_func(inputstates) == 0)

def not_func(inputstates):
    """Invert single input"""
    assert len(inputstates) <= 1, (
        f"not_func must have 0,1 inputs. Got {len(inputstates)}" )
    if len(inputstates) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in inputstates]
    return int(inputstates[0] == 0)

def mj_func(inputstates):
    """Majority of inputs are non-zero"""
    return int(len([v for v in inputstates if v > 0]) > len(inputstates)/2)
majority_func=mj_func

def mn_func(inputstates):
    """Minority of inputs are non-zero"""
    return int(len([v for v in inputstates if v > 0]) <= len(inputstates)/2)
minority_func=mn_func

def min_func(inputstates):
    """Minimum state of inputs"""
    return min(inputstates)

def parity_func(inputstates):
    return sum(inputstates) % 2


