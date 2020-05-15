#! /usr/bin/env python
# Python standard library
import sys
import argparse
import logging
from datetime import datetime
import json
import platform
# External packages
import pandas as pd
import matplotlib.pyplot as plt
import itertools as it
import numpy as np
# Local packages
import phial.toolbox as tb
import phial.node_functions as nf
import phial.gen_funcs as gf
from phial.utils import tic,toc,Timer


class AllPerms():  # modified from earlier AllPerms to remove redundant rows from LUT
    # create a node set with all possible binary responses
    def __init__(self, N, name=''):
        # N is the number of inputs to the node
        self.N = N
        self.permutations = 2**(N+1)

        self.indices = set([sum(k) for k in it.product([0,1], repeat=N)])  
        self.name = name
        LUT = []
        for k in range(self.permutations):
            nn = [int(i) for i in list('{0:016b}'.format(k))]
            nn.reverse()
            LUT.append([nn[k] for k in self.indices])
        self.lut = np.array(LUT).T

    def __call__(self, n):
        # n is the node-function index
        def node(inputs):
            # inputs is a binary tuple of node inputs
            if (len(inputs) != self.N):
                txt = 'this function group requires a tuple with {} inputs: {} supplied'.\
                format(self.N, len(inputs))
                raise ValueError(txt)
            return self.lut[sum(inputs), n]
        return node


def gen_truth_funcs(map_node_argcnt): 
    """map_node_argcnt: d[nodeLabel] = numArgs
    RETURN: d[nodeLabel] = [func1(inputs), func2(inputs), ... ]
    """
    objs = [AllPerms(k) for k in set(map_node_argcnt.values())]
    
    funcs = dict()
    for j in objs:
        funcs[j.N] = [j(k) for k in range(j.permutations)]
    out = dict()
    for j, k in map_node_argcnt.items():
        out[j] = funcs[k]

    return out


# nodes are extracted from edges.  This means an experiment cannot contain
# a node that has no edges. (self edge is ok)
class Experiment():
    def __init__(self, edges,
                 title='',
                 comment=None,
                 funcs={}, # dict[nodeLabel] = func
                 states={}, # dict[nodeLabel] = numStates
                 net = None,
                 default_statesPerNode=2,
                 default_func=nf.MJ_func):
        """Nodes not given as keys to funcs dict default to 'default_func'"""
        self.results = {}
        self.filename = None
        self.starttime = None
        self.elapsed = None

        if net is not None:
            self.net = net
        else:
            self.net = tb.Net(edges=edges, title=title,
                              SpN=default_statesPerNode,
                              func=default_func)
        self.title = title
        for label,func in funcs.items():
            self.net.get_node(label).func = func
        for label,num in states.items():
            self.net.get_node(label).num_states = num

    def _make_func_lists(self):
        nargs_set= set([len(list(self.net.graph.predecessors(n.label)))
                        for n in self.net.nodes])
        self.func_table = dict() # d[N] = [func1,func2, ..., func(4^N)]
        for N in nargs_set:
            self.func_table[N] = gf.gen_funcs(N)

    @property
    def get_num_funcs(self):
        """Experimenter uses this to get the count of functions available for
        each node.  She uses the count in call to `gen_tpm` to assign 
        one of the available functions to selected nodes.
        """
        self._make_func_lists()
        nnf = dict() # dd[nodeLabel] => numberOfFuncs
        for n in self.net.nodes:
            nargs = len(list(self.net.graph.predecessors(n.label)))
            nnf[n.label] = len(self.func_table[nargs])
        return nnf

    def gen_tpm(self, node_func_idx):
        """Assign funcs to nodes, then create system TPM.
        node_func_idx:: d[nodeLabel] = funcIndex"""
        for label,idx in node_func_idx.items():
            N = len(list(self.net.graph.predecessors(label)))
            funcidx = node_func_idx[label]
            self.net.get_node(label).func = self.func_table[N][funcidx]
        self.net.tpm = self.net.calc_tpm()
        return self.net.tpm
    
    def info(self):
        dd = dict(
            timestamp = str(self.starttime),
            duration = self.elapsed, # seconds
            results = self.results,
            filename = self.filename,
            uname = platform.uname(),
        )

        return dd
        
    def run(self, verbose=False, plot=False, **kwargs):
        timer0 = Timer()
        timer1 = Timer()
        timer0.tic # start tracking time
        self.starttime = datetime.now()

        # Calculate!
        for s in self.net.out_states:
            timer1.tic 
            phi = self.net.phi(s)
            secs = timer1.toc
            self.results[s] = dict(phi=phi, elapsed_seconds=secs)
            if verbose:
                print(f"Calculated Φ = {phi} using state={s} in {secs} seconds")
        self.elapsed = timer0.toc  # Seconds since start
        if plot:
            self.analyze(**kwargs)

    def analyze(self, figsize=(14,4), countUnreachable=False):
        dd = dict((s,v['phi']) for s,v in self.results.items())
        if countUnreachable:
            dd.update(dict((s,-1) for s in self.net.unreachable_states))
        plt.rcParams['figure.figsize'] = figsize
        fig, ax = plt.subplots(1,2)
        self.net.draw()
        #df=self.net.tpm

        dff = pd.DataFrame(dd.items())
        hist = dff.hist(bins=100, ax=ax[0])
        fig.suptitle(self.title)
        
##############################################################################

def main():
    #print('EXECUTING: {}\n\n'.format(' '.join(sys.argv)))
    parser = argparse.ArgumentParser(
        #!version='1.0.1',
        description='My shiny new python program',
        epilog='EXAMPLE: %(prog)s a b"'
        )
    dflt_func = 'XOR'
    dflt_spn = 2
    parser.add_argument('net',
                        help=('Net definition in JSON format containing '
                              'at least "edges" key. '
                              'Optional keys: "funcs", "title"') )
    parser.add_argument('--default_func',
                        default=dflt_func,
                        help=('Default function '
                              'when not explicitly specified for a node.'))
    parser.add_argument('--SpN',
                        default=dflt_spn,
                        help=('Default number of states per node '
                              'when not explicitly specified for a node.'))
    parser.add_argument('--outfile', help='File to save experiment into',
                        type=argparse.FileType('w') )
    parser.add_argument('--loglevel',      help='Kind of diagnostic output',
                        choices = ['CRTICAL','ERROR','WARNING','INFO','DEBUG'],
                        default='WARNING',
                        )
    args = parser.parse_args()
    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel) 
    logging.basicConfig(level = log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M'
                        )
    #logging.debug('Debug output is enabled!!!')
    with open(args.net, 'r') as f:
        jj = json.load(f)
    funcs = dict((node,nf.funcLUT.get(func,nf.MJ_func))
                 for node,func in jj.get('funcs').items())
    exp = Experiment(jj.get('edges',[]),
                     funcs = funcs,
                     default_statesPerNode = args.SpN,
                     default_func = nf.funcLUT.get(args.default_func,nf.MJ_func))
    exp.run()
    res = exp.info()
    answers = ', '.join([f'{s}={phi}' for (s,phi) in res['results'].items()])
    print(f"""# EXPERIMENT: {jj.get('title','')}
Time Started      {res['timestamp']}
Duration (sec)    {res['duration']}
Results (state,ϕ) {answers}
Net configuration {jj}       
""")


if __name__ == '__main__':
    main()
        
