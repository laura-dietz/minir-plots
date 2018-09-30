from __future__ import print_function

import os
import matplotlib as mpl
mpl.use("Agg")

from math import sqrt
import numpy as np
import math
from pandas.util.testing import DataFrame, Series
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import pairedttest

__author__ = 'dietz'

from argparse import ArgumentParser

# query metric value
# C09-1 ndcg    0.27478
# C09-1 ndcg5   0.47244
# C09-1 ndcg10  0.32972
# C09-1 ndcg20  0.25703
# C09-1 ERR     0.18652
# C09-1 ERR10   0.16907
# C09-1 ERR20   0.17581
# C09-1 P1      1.00000

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

tooldescription = """
Classic bar chart indicating the mean of values for the given
metric across all queries with error bars indicating the standard
error.
"""
parser = ArgumentParser(description=tooldescription)
parser.add_argument('--out', help='outputfilename', metavar='FILE',  required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--format', help='trec_eval output or galago_eval output', default='trec_eval')
parser.add_argument('-c', help='instead of average, also count non-existing queries', default=False, action='store_true')
parser.add_argument('--sort', help='sort methods in plot', action='store_true', default=False)
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))



def main():
        def read_ssv(fname):
            lines = [line.split() for line in open(fname, 'r')]
            if args.format.lower() == 'galago_eval':
                return lines
            elif args.format.lower() == 'trec_eval':
                return [[line[1], line[0]] + line[2:] for line in lines]


        def readNumQueries(run):
            tsv = read_ssv(run)
            data = [int(row[2]) for row in tsv if row[0] == "all" and row[1] == numQueries_key]
            return data[0]


        def findQueriesWithNanValues(run):
            tsv = read_ssv(run)
            # print ("tsv,", tsv)
            queriesWithNan = {row[0] for row in tsv if row[1] == 'num_rel' and (float(row[2]) == 0.0 or math.isnan(float(row[2])))}
            return queriesWithNan

        def fetchValues(run):
            tsv = read_ssv(run)
            data = {row[0]: float(row[2]) for row in tsv if row[1] == args.metric and not math.isnan(float(row[2]))}
            return data

        args = parser.parse_args()

        pairedt = pairedttest.pairedt(best=True, format=args.format, metric=args.metric, runs=args.runs)
        print("paired t")
        print(pairedt)
        print("=-----=")

        numQueries_key = "num_q"
        print("column.py metric="+args.metric+" out="+args.out)
        
        datas = {run: fetchValues(run) for run in args.runs}
        
        # deal with nans
        queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
        basedata=datas[args.runs[0]]
        queries = set(basedata.keys()).difference(queriesWithNanValues)
        numQueries = readNumQueries(args.runs[0]) if args.c else len(queries)
        
        seriesDict = {'mean':dict(), 'stderr':dict()}
        
        
        for run in datas:
            data = datas[run]
            
            if sum(not key in data for key in queries) > 0:
                print("data for run "+run+" does not contain all queries "+" ".join(queries))

            mean = np.sum([data.get(key, 0.0) for key in queries]) / numQueries
            stderr = np.std([data.get(key, 0.0) for key in queries] + ([0.0]* (numQueries - len(queries)))) / sqrt(numQueries)
            seriesDict['mean'][run]=mean
            seriesDict['stderr'][run]=stderr




        print( "dropping queries because of NaN values: "+ " ".join(queriesWithNanValues))

        print ('\t'.join(['run', 'mean/stderr']))
        for run in datas:
            #if not run == args.runs[0]:
            print ('\t'.join([run, str(seriesDict['mean'][run]), str(seriesDict['stderr'][run])]))


        df1 = DataFrame(seriesDict, index=pd.Index(args.runs))
        if args.sort:
                df1.sort_values('mean',ascending=False,inplace=True) 
        df2 = df1['mean']
        df2.index=[os.path.basename(label) for label in df1.index]
        df1.index=[os.path.basename(label) for label in df1.index]

        print('df2.index=',df2.index)

        df2.text=['**' if (math.isnan(pairedt[label][1]) or pairedt[label][1]>0.05) else '' for label in df2.index]
        min_same_idx = max( [i if (math.isnan(pairedt[label][1]) or pairedt[label][1]>0.05) else 0 for i,label in enumerate(df2.index)])


        cs = {k:v for k,v in zip(sorted(list(set([label[0:3] for label in df1.index]))), itertools.cycle(['0.1','0.9','0.5','0.3','0.7','0.2','0.8', '0.4','0.6'])) }
        df1['color']=[cs[label[0:3]] for label in df1.index]
        print(df1['color'])
        plt.tick_params(colors=df1.color)
        fig, ax = plt.subplots()


        df2.plot.bar(yerr = df1['stderr'], color=df1.color.values,  ax=ax)

        for (p, i) in zip(ax.patches,range(100)):
            #print ('p', p, df2.index[i])
            #ax.annotate(df2.text[i], xy=(p.get_x() + p.get_width() / 2.0, p.get_height()*0.9), ha='center', va='center',)

            if i==min_same_idx:
                frompoint=(p.get_x()+p.get_width(), p.get_height()/2.0)
                topoint=(0.0-p.get_width()/2.0, p.get_height()/2.0)
                ax.annotate("",
                            xy=topoint, xycoords='data',
                            xytext=frompoint, textcoords='data',
                            arrowprops=dict(arrowstyle="<|-|>",
                                            connectionstyle="arc3", ec='r'),
                            )
        ax.grid()
        plt.ylabel(args.metric, fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.xticks(rotation=90)
        plt.savefig(args.out, bbox_inches='tight')

        # plt.show()

if __name__ == '__main__':
    main()


