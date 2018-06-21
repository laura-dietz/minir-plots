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

__author__ = 'dietz'

from argparse import ArgumentParser

# query metric value
# C09-1	ndcg	0.27478
# C09-1	ndcg5	0.47244
# C09-1	ndcg10	0.32972
# C09-1	ndcg20	0.25703
# C09-1	ERR	0.18652
# C09-1	ERR10	0.16907
# C09-1	ERR20	0.17581
# C09-1	P1	1.00000

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

tooldescription = """
Classic bar chart indicating the mean of values for the given
metric across all queries with error bars indicating the standard
error.  (Run file is a misnomer, it should be called eval file, because it is
the output of trec_eval -c -q)
"""
parser = ArgumentParser(description=tooldescription)
parser.add_argument('--out', help='outputfilename', metavar='FILE',  required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--format', help='trec_eval output or galago_eval output', default='trec_eval')
parser.add_argument('-c', help='instead of average, also count non-existing queries', default=False, action='store_true')
parser.add_argument('--sort', help='sort methods in plot', action='store_true', default=False)
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

numQueries_key = "num_q"

print("column.py metric="+args.metric+" out="+args.out)

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


df1 = DataFrame(seriesDict, index=args.runs)
if args.sort:
	df1.sort_values('mean',ascending=False,inplace=True) 
df2 = df1['mean']
df2.index=[os.path.basename(label) for label in df1.index]

fig, ax = plt.subplots()
#plt.figure()
df2.plot(kind='bar', yerr = df1['stderr'], color=['0.0', '0.6', '0.4', '0.8','0.0', '0.6', '0.4', '0.8','0.0', '0.6', '0.4', '0.8'], ax=ax )
ax.grid()
plt.ylabel(args.metric, fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=20)
plt.xticks(rotation=90)
plt.savefig(args.out, bbox_inches='tight')

# plt.show()
