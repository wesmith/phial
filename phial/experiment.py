#! /usr/bin/env python
"""**NB:** To use the graph DRAW methods, you must have graphviz installed.
https://www.graphviz.org/"""
# Python standard library
import sys
import argparse
import logging
from datetime import datetime,date
import json
import platform
from pprint import pprint
from pathlib import Path
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


# nodes are extracted from edges.  This means an experiment cannot contain
# a node that has no edges. (self edge is ok)
class Experiment():
    """Setup, run, analyze IIT experiments.

    Nodes not given as keys to funcs dict default to 'default_func'
    
    :param edges: connectivity edges; e.g. [(0,1), (1,2), (2,0)]
    :param title: Label for experiment
    :param comment: Additional reports associated with experiment

    :param funcs: dict[nodeLabel] = func; func can be python function or 
        a stripped name from library (node_functions.py) e.g. 'XOR'.
    :param states: dict[nodeLabel] = numStatesForNode
    :param net: Net instance that defines network used for experiment
    :param saveDir: directory to save experiment results into.
    :param default_statesPerNode: default number of States per Node
    :param default_func: default function (mechanism) for all nodes
    """

    def __init__(self, edges,
                 title='',
                 comment=None,
                 funcs={}, # dict[nodeLabel] = func
                 states={}, # dict[nodeLabel] = numStates
                 net = None,
                 saveDir = Path.home() / 'phial',
                 default_statesPerNode=2,
                 default_func=nf.MJ_func):
        self.results = {}
        self.filename = None
        self.starttime = None
        self.elapsed = None
        self.saveDir = Path(saveDir).expanduser()

        if net is not None:
            self.net = net
        else:
            self.net = tb.Net(edges=edges, title=title,
                              SpN=default_statesPerNode,
                              func=default_func)
        self.title = title
        for label,func in funcs.items():
            if type(func) == str:
                func = nf.func_from_name(func)
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
        each node.  She uses the count in call to ``gen_tpm`` to assign 
        one of the available functions to selected nodes.

        :returns: dict[nodeLabel] => numFuncs
        :rtype: dict

        """
        self._make_func_lists()
        nnf = dict() # dd[nodeLabel] => numberOfFuncs
        for n in self.net.nodes:
            nargs = len(list(self.net.graph.predecessors(n.label)))
            nnf[n.label] = len(self.func_table[nargs])
        return nnf

    def gen_tpm(self, node_func_idx):
        """Assign funcs to nodes, then (re)create system TPM.

        Use ``get_num_funcs`` to find the how many functions are available for 
        each node. (the max idx is count-1)

        :param node_func_idx: d[nodeLabel] = funcIndex
        :returns: tpm
        :rtype: pandas.DataFrame

        """
        for label,idx in node_func_idx.items():
            N = len(list(self.net.graph.predecessors(label)))
            funcidx = node_func_idx[label]
            self.net.get_node(label).func = self.func_table[N][funcidx]
        self.net.tpm = self.net.calc_tpm()
        return self.net.tpm
    
    def info(self):
        """Info about network and  results.

        :returns: dict with keys: timestamp, duration, results, uname
        :rtype: dict
        """
        dd = dict(
            timestamp = str(self.starttime),
            duration = self.elapsed, # seconds
            results = self.results,
            connected_components = self.net.state_cc,
            cycles = len(list(self.net.state_cycles)),
            filename = self.filename,
            uname = platform.uname(),
        )
        return dd
        

    def run(self, verbose=False, plot=False, save=True, **kwargs):
        """Calculate big-phi for all reachable states over network defined 
        in this instance.

        :param verbose: Runtime info on what is being done
        :param plot: Plots analysis of results
        :param save: if True save experiment to auto-generated name. If str, save to that basename in `saveDir`
        :returns: info about results
        :rtype: dict

        """
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
        if save:
            if type(save) == str:
                self.save(self.saveDir/f'{save}.json')
            else:
                self.save()
        return self.info()

    def save(self, filename=None):
        """Save experiment setup and results to file.

        :param filename: Save here. If not given, invent one that includes a date-time stamp in the name
        :returns: 
        :rtype: 

        """
        #now=datetime.now().isoformat(timespec='seconds')
        now=datetime.now().isoformat()
        fname = filename or self.saveDir/f'results_{now}.json'

        out = dict(net=self.net.to_json(),
                   results=self.info() )
        with open(fname, 'w') as f:
            #!json.dump(out, indent=2, fp=f)
            json.dump(out, fp=f)
        print(f'Saved experiment with results to: {fname}')
        return fname
    
    def analyze(self, figsize=(14,4), countUnreachable=False):
        """Analyze and plot results.

        :param figsize: (width,height) of plot
        :param countUnreachable: Histogram includes in-states that fail phi-calc
        :returns: None
        :rtype: None

        """
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
def my_parser():
    prog = sys.argv[0]
    parser = argparse.ArgumentParser(
        #!version='1.0.1',
        description='Run an IIT experiment',
        epilog=f'EXAMPLE: {prog} my_network.json"'
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
    return parser
    
def main():
    #print('EXECUTING: {}\n\n'.format(' '.join(sys.argv)))
    parser = my_parser()
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
        
