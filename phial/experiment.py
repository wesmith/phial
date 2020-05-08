#! /usr/bin/env python
import sys, argparse, logging
import pandas as pd
import matplotlib.pyplot as plt
import sys
import phial.toolbox as tb


def get_net(ledges, nodes, funcs, title=''):
    # wrapper for SP tools
    i, j = zip(*ledges)
    indexLUT = dict([(l,ord(l)-ord(nodes[0])) for l in sorted(set(i+j))])
    edges = [(indexLUT[i],indexLUT[j]) for i,j in ledges]
    net = tb.Net(edges=edges, title=title)
    for j,k in zip(nodes, funcs):
        net.get_node(j).func = k
    return net

def get_phi(perm, net):
    try:
        return net.phi(perm)
    except:
        return -1 # state isn't reachable

def run_expt(edges, nodes, funcs, title='', figsize=(14,4), clean=True):
    plt.rcParams['figure.figsize'] = figsize
    if clean: # remove pyphi output from stdout
        orig_stdout = sys.stdout
        log = open("del.log", "a")
        sys.stdout = log
    net = get_net(edges, nodes, funcs, title=title)
    fig, ax = plt.subplots(1,2)
    net.draw()
    df=net.tpm
    dd = [(k, get_phi(k, net)) for k in df.index]
    dff = pd.DataFrame(dd)
    hist = dff.hist(bins=100, ax=ax[0])
    fig.suptitle(title)
    if clean:  # reset stdout
        sys.stdout = orig_stdout
        log.close()



##############################################################################

def main():
    print('EXECUTING: {}\n\n'.format(' '.join(sys.argv)))
    parser = argparse.ArgumentParser(
        #!version='1.0.1',
        description='My shiny new python program',
        epilog='EXAMPLE: %(prog)s a b"'
        )
    parser.add_argument('infile',  help='Input file',
                        type=argparse.FileType('r') )
    parser.add_argument('outfile', help='Output output',
                        type=argparse.FileType('w') )
    parser.add_argument('-q', '--quality', help='Processing quality',
                        choices=['low','medium','high'], default='high')
    parser.add_argument('--loglevel',      help='Kind of diagnostic output',
                        choices = ['CRTICAL','ERROR','WARNING','INFO','DEBUG'],
                        default='WARNING',
                        )
    args = parser.parse_args()
    #!args.outfile.close()
    #!args.outfile = args.outfile.name

    #!print 'My args=',args
    #!print 'infile=',args.infile


    log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(log_level, int):
        parser.error('Invalid log level: %s' % args.loglevel) 
    logging.basicConfig(level = log_level,
                        format='%(levelname)s %(message)s',
                        datefmt='%m-%d %H:%M'
                        )
    logging.debug('Debug output is enabled!!!')


    myFunc(args.infile, args.outfile)

if __name__ == '__main__':
    main()
        
