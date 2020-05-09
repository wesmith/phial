"""To use the graph DRAW methods, you must have graphviz installed.
https://www.graphviz.org/
"""
# Python standard library
from collections import Counter, defaultdict
import itertools
from random import choice
# External packages
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from networkx.drawing.nx_pydot import pydot_layout
import pandas as pd
import numpy as np
import pyphi
import pyphi.network
# Local packages
import phial.node_functions as nf


# NB: This does NOT hold the state of a node.  That would increase load
# on processing multiple states -- each with its own set of nodes!
# Instead, a statestr contains states for all nodes a specific time.
#
# Would this be light-weight enough 10^5++ nodes? @@@
#
# InstanceVars: id, label, num_states, func
class Node():
    """Node in network. Supports more than just two states but downstream 
    software may be built for only binary nodes. Auto increment node id that 
    will be used as label if one isn't provided on creation.
    """
    _id = 0

    def __init__(self,label=None, num_states=2, id=None, func=nf.MAZ_func):
        if id is None:
            id = Node._id
            Node._id += 1
        self.id = id
        self.label = label or id
        self.num_states = num_states
        self.func = func 
        
    @property
    def random_state(self):
        return choice(range(self.num_states))

    @property
    def states(self):
        """States supported by this node."""
        return range(self.num_states)

    def __repr__(self):
        return ('Node('
                f'label={self.label}, '
                f'id={self.id}, '
                f'num_states={self.num_states}, '
                f'func={self.func}')

    def __str__(self):
        return f'{self.label}({self.id}): {self.num_states},{self.func.__name__}'

class Net():
    """Store everything needed to calculate phi.
    InstanceVars: graph, node_lut"""

    nn = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
    
    def __init__(self,
                 edges = None, # connectivity edges; e.g. [(0,1), (1,2), (2,0)]
                 N = 5, # Number of nodes
                 #graph = None, # networkx graph
                 #nodes = None, # e.g. list('ABCD')
                 #cm = None, # connectivity matrix
                 SpN = 2,  # States per Node
                 title = None, # Label for graph
                 func = nf.MAZ_func, # default mechanism for all nodes
                 ):
        G = nx.DiGraph()
        if edges is None:
            n_list = range(N)
        else:
            i,j = zip(*edges)
            maxid = max(i+j)
            n_list = sorted(set(i+j))
        edgesStrP = type(n_list[0]) == str
        if edgesStrP:
            n_list = [(ord(l) - ord('A')) for l in n_list]
        nodes = [Node(id=i, label=Net.nn[i], num_states=SpN, func=func)
                 for i in n_list]

        # lut[label] -> Node
        self.node_lut = dict((n.label,n) for n in nodes)
        #invlut[i] -> label
        invlut = dict(((n.id,n.label) for n in self.node_lut.values())) 
            
        G.add_nodes_from(self.node_lut.keys())
        if edges is not None:
            if edgesStrP:
                G.add_edges_from(edges)
            else:
                G.add_edges_from([(invlut[i],invlut[j]) for (i,j) in edges])
        self.graph = G
        self.graph.name = title
        self.tpm_df = self.tpm


    def info(self):
        dd = dict(
            edges=list(self.graph.edges),
            nodes=[str(n) for n in self.nodes],
            num_unreachable_states=len(self.unreachable_states),
        )
        return dd
        
    def node_state_counts(self, node):
        """Truth table of node.func run over all possible inputs.
        Inputs are predecessor nodes with all possible states."""
        preds = (self.get_node(l)
                 for l in set(self.graph.predecessors(node.label)))
        counter = Counter()
        counter.update(node.func(sv)
                       for sv in itertools.product(*[n.states for n in preds]))
        return counter

    def eval_node(self, node, system_state_tup):
        preds_id = set([self.get_node(l).id
                    for l in set(self.graph.predecessors(node.label))])
        args = [system_state_tup[i] for i in preds_id]
        return node.func(args)
        

    def node_pd(self, node):
        """Probability Distribution of NODE states given all possible inputs
        constrained by graph."""
        #node = self.get_node(node_label)
        counts = self.node_state_counts(node)
        total = sum(counts.values())
        return [counts[i]/total for i in node.states]

    @property
    def tpm(self):
        """Iterate over all possible states(!!!) using node funcs
        to calculate output state. State-to-State form. Allows non-binary"""
        backwards=True  # I hate the order the papers use!!
        allstates = list(itertools.product(*[n.states for n in self.nodes]))
        N = len(self.nodes)
        allstatesstr = [''.join([f'{s:x}' for s in sv]) for sv in allstates]
        df = pd.DataFrame(index=allstatesstr,
                          columns=[n.label for n in self.nodes]).fillna(0)
        
        for sv in allstates:
            s0 = ''.join(f'{s:x}' for s in sv)
            for i in range(N):
                node = self.nodes[i]
                nodestate = self.eval_node(node,sv)
                df.loc[s0,node.label] =  nodestate

        if backwards:
            newindex= sorted(df.index, key= lambda lab: lab[::-1])
            return df.reindex(index=newindex)
        return df

    @property
    def out_states(self):
        """Output states of TPM in hexstr form. These are the states allowed
        for the 'statestr' phi method.
        Otherwise the error 'cannot be reached in the given TPM' is thrown."""
        return set(''.join(f'{s:x}' for s in self.tpm.iloc[i])
                   for i in range(self.tpm.shape[0]))
    @property
    def in_states(self):
        return self.tpm.index

    @property
    def unreachable_states(self):
        """System states that are not reachable from any input states."""
        return sorted(set(self.in_states) - self.out_states)
        

    def nodes_to_tpm(self, verbose=False):
        """Iterate over all possible states(!!!) using node funcs
        to calculate output state. State-to-Node form. binary nodes only"""
        transitions = defaultdict(int) # transitions[(s0,s1)] => count
        allstates = list(itertools.product(*[n.states for n in self.nodes]))
        for sv in allstates:
            s0 = ''.join(f'{s:x}' for s in sv)
            sv1 = list(sv)
            for i in range(len(sv)):
                node = self.nodes[i]
                cnt = self.node_state_counts(node)
                for nodestate in node.states:
                    sv1[i] = nodestate
                    s1 = ''.join(f'{s:x}' for s in sv1)
                    transitions[(s0,s1)] += cnt[nodestate]
            # pad because pyphi requires full matrix
            for sv1 in allstates:
                s1 = ''.join(f'{s:x}' for s in sv1)                
                transitions[(s0,s1)] += 0

        # Convert counts to DF
        allstatesstr = [''.join([f'{s:x}' for s in sv]) for sv in allstates]
        allnodes = [n.label for n in self.nodes()]
        df = pd.DataFrame(index=allstatesstr, columns=allnodes).fillna(0)
        for ((s0,s1),count) in transitions.items():
            df.loc[s0,s1] =  df.loc[s0,s1] + count
            
        # return normalized form
        return df.fillna(0)
    
    @property
    def cm(self):
        return nx.to_numpy_array(self.graph)

    @property
    def df(self):
        return nx.to_pandas_adjacency(self.graph, nodelist=self.node_labels)

    @property
    def nodes(self):
        """Return list of all nodes in ID order."""
        return sorted(self.node_lut.values(), key=lambda n: n.id)

    @property
    def node_labels(self):
        return [n.label for n in self.node_lut.values()]

    def __Xsuccessors(self, node_label):
        return list(self.graph.neighbors(node_label))

    def get_node(self, node_label):
        return self.node_lut[node_label]

    def get_nodes(self, node_labels):
        return [self.node_lut[label] for label in node_labels]
    
    def __len__(self):
        return len(self.graph)

    def graph(self, pngfile=None):
        """Return networkx DiGraph. Maybe write to PNG file."""
        G = nx.DiGraph(self.graph)
        if pngfile is not None:
            dotfile = pngfile + ".dot"
            write_dot(G, dotfile)
            cmd = (f'dot -Tpng -o{pngfile} {dotfile} ')
            with open(pngfile,'w') as f:
                subprocess.check_output(cmd, shell=True)
        return G

    def draw(self):
        nx.draw(self.graph,
                pos=pydot_layout(self.graph),
                # label='gnp_random_graph({N},{p})',
                with_labels=True )
        return self

    @property
    def pyphi_network(self):
        """Return pyphi Network() instance."""
        return pyphi.network.Network(self.tpm.to_numpy(),
                                     cm=self.cm,
                                     node_labels=self.node_labels)

    def phi(self, statestr=None):
        """Calculate phi for net."""
        if statestr is None:
            instatestr = choice(self.tpm_df.index)
            statestr = ''.join(f'{s:x}' for s in self.tpm_df.loc[instatestr,:])
        state = [int(c) for c in list(statestr)] 
        print(f'Calculating Φ at state={state}')
        node_indices = tuple(range(len(self.graph)))
        subsystem = pyphi.Subsystem(self.pyphi_network, state, node_indices)
        return pyphi.compute.phi(subsystem)

def phi_all_states(net):
    """Run pyphi.compute.phi over all reachable states in net."""
    results = dict() # d[state] => phi
    for statestr in net.out_states:
        results[statestr] = net.phi(statestr)
        print(f"Φ = {results[statestr]} using state={statestr}")
    return results

