import itertools as it

# https://docs.python.org/3/library/itertools.html?highlight=product#itertools.product
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(len(s)+1))

def func_from_true_states(true_states, N=999):
    """RETURN a binary function of N inputs such that iff function inputs
    match on of true_states then output is 1."""
    def binary_func(inputs):
        assert len(inputs) == N, f'Function requires {N} args, got {len(inputs)}'
        return int(tuple(inputs) in true_states)
    binary_func.true_states = true_states # info only
    return binary_func


def gen_funcs(N):
    """Generate all possible 4^N binary functions of N binary inputs.
    Num in-states = 2^N.
    Functions include all (2^2^N) possible ouputs for those in-states.
    RETURN: list of functions, f(inputs)=>0,1

    >>> len(gen_funcs(2))
    16
    >>> gen_funcs(2)[8].true_states  # XOR
    ((0, 1), (1, 0))
    >>> gen_funcs(2)[8]([1,0])         # run XOR
    1
    """
    return [func_from_true_states(true_states, N=N)
            for true_states in powerset(it.product([0,1], repeat=N))]
    

    
