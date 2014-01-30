import csv
from math import sqrt
import os
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
        return arg# open(arg,'r')  #return an open file handle


parser = ArgumentParser()
parser.add_argument('--out', help='outputfilename', metavar='FILE',  required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

print "column.py metric="+args.metric+" out="+args.out

# with open(args.run1,'rb') as tsv1, open(args.run2, 'rb') as tsv2:


def findQueriesWithNanValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    queriesWithNan = {row[0] for row in tsv if row[1] == 'num_rel' and (float(row[2]) == 0.0 or math.isnan(float(row[2])))}
    return queriesWithNan

def fetchValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    data = {row[0]: float(row[2]) for row in tsv if row[1] == args.metric and not math.isnan(float(row[2]))}
    return data


datas = {run: fetchValues(run) for run in args.runs}

# deal with nans
queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
basedata=datas[args.runs[0]]
queries = set(basedata.keys()).difference(queriesWithNanValues)

seriesDict = {'mean':dict(), 'stderr':dict()}


for run in datas:
    data = datas[run]

    if sum(not key in data for key in queries) > 0:
        print "data for run "+run+" does not contain all queries "+" ".join(queries)

    mean = np.average([data[key] for key in queries])
    stderr = np.std([data[key] for key in queries]) / sqrt(len(queries))
    seriesDict['mean'][run]=mean
    seriesDict['stderr'][run]=stderr




print "dropping queries because of NaN values: "+ " ".join(queriesWithNanValues)

print '\t'.join(['run', 'mean/stderr'])
for run in datas:
    if not run == args.runs[0]:
        print '\t'.join([run, str(seriesDict['mean'][run]), str(seriesDict['stderr'][run])])


df1 = DataFrame(seriesDict, index=args.runs)
df2 = df1['mean']
df2.index=[os.path.basename(label) for label in df1.index]


plt.figure()
df2.plot(kind='bar', yerr = df1['stderr'], color=['1.0', '0.80', '0.4', '0.0', '0.70'])
plt.ylabel(args.metric, fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=20)
plt.xticks(rotation=0)
plt.savefig(args.out, bbox_inches='tight')

# plt.show()
