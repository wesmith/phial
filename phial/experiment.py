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
# Local packages
import phial.toolbox as tb
import phial.node_functions as nf
from phial.utils import tic,toc

#! def get_net(ledges, nodes, funcs, title=''):
#!     # wrapper for SP tools
#!     i, j = zip(*ledges)
#!     indexLUT = dict([(l,ord(l)-ord(nodes[0])) for l in sorted(set(i+j))])
#!     edges = [(indexLUT[i],indexLUT[j]) for i,j in ledges]
#!     net = tb.Net(edges=edges, title=title)
#!     for j,k in zip(nodes, funcs):
#!         net.get_node(j).func = k
#!     return net
#! 
#! def get_phi(perm, net):
#!     try:
#!         return net.phi(perm)
#!     except:
#!         return -1 # state isn't reachable
#! 
#! def run_expt(edges, nodes, funcs, title='', figsize=(14,4), clean=True):
#!     plt.rcParams['figure.figsize'] = figsize
#!     if clean: # remove pyphi output from stdout
#!         orig_stdout = sys.stdout
#!         log = open("del.log", "a")
#!         sys.stdout = log
#!     net = get_net(edges, nodes, funcs, title=title)
#!     fig, ax = plt.subplots(1,2)
#!     net.draw()
#!     df=net.tpm
#!     dd = [(k, get_phi(k, net)) for k in df.index]
#!     dff = pd.DataFrame(dd)
#!     hist = dff.hist(bins=100, ax=ax[0])
#!     fig.suptitle(title)
#!     if clean:  # reset stdout
#!         sys.stdout = orig_stdout
#!         log.close()


# nodes are extracted from edges.  This means an experiment cannot contain
# a node that has no edges. (self edge is ok)
class Experiment():
    def __init__(self, edges,
                 title='',
                 comment=None,
                 funcs={}, # dict[nodeLabel] = func
                 states={}, # dict[nodeLabel] = numStates
                 default_statesPerNode=2,
                 default_func=nf.MJ_func):
        """Nodes not given as keys to funcs dict default to 'default_func'"""
        self.net = tb.Net(edges=edges, title=title,
                          SpN=default_statesPerNode,
                          func=default_func)
        self.title = title
        for label,func in funcs.items():
            self.net.get_node(label).func = func
        for label,num in states.items():
            self.net.get_node(label).num_states = num
        self.results = None
        self.filename = None

    def info(self):
        dd = dict(
            timestamp = str(self.starttime),
            duration = self.elapsed, # seconds
            results = self.results,
            filename = self.filename,
            uname = platform.uname(),
        )

        return dd
        
    def run(self, figsize=(14,4), clean=True, countUnreachable=False):
        tic() # start tracking time
        self.starttime = datetime.now()
        plt.rcParams['figure.figsize'] = figsize
        if clean: # remove pyphi output from stdout
            orig_stdout = sys.stdout
            log = open("del.log", "a")
            sys.stdout = log
        fig, ax = plt.subplots(1,2)
        self.net.draw()
        df=self.net.tpm
        #dd = [(k, get_phi(k, net)) for k in df.index]
        dd = dict((s, self.net.phi(s)) for s in self.net.out_states)
        if countUnreachable:
            dd.update(dict((s,-1) for s in self.net.unreachable_states))
        dff = pd.DataFrame(list(dd.items()))
        hist = dff.hist(bins=100, ax=ax[0])
        fig.suptitle(self.title)
        if clean:  # reset stdout
            sys.stdout = orig_stdout
            log.close()
        self.results = dd
        self.elapsed = toc()  # Seconds since start
        
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
        
