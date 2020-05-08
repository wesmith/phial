from functools import reduce
import operator


def noop_func(args):
    """Ignore args"""
    return 0 # must return some state and we know there is at least one

def ma_func(args):
    """Mean Activation as state. Upto 15"""
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    return min(15, int(sum(args)/len(args)))
copy_func = ma_func #  Indended to have exactly one input node. 

def maz_func(args):
    """Mean Activation gt zero"""
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    return int((sum(args)/len(args)) > 0)

def tri_func(args):
    """Count input states. Produces 3 states"""
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    if sum(args) == 0:
        return 0
    if sum(args) == 1:
        return 1
    else:
        return 2

def or_func(args):
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in args]
    return int(reduce(operator.or_, invals)    )

# In published papers, COPY seems to assume exactly one in-edge
def copy_func(args):
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in args]
    return int(reduce(operator.or_, invals))

def xor_func(args):
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in args]
    return int(reduce(operator.xor, invals))

def and_func(args):
    if len(args) == 0:
        return 0 # must return some state and we know there is at least one
    invals = [v != 0 for v in args]
    return int(reduce(operator.and_, invals))
