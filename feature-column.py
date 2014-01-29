from collections import defaultdict
import csv
from math import sqrt
from numpy.testing import rand
import os
import numpy as np
import math
from pandas.util.testing import DataFrame, Series
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import ylabel

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
parser.add_argument('--out', help='outputfilename', required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--names', help='filename for names lookup', required=True,type=lambda x: is_valid_file(parser, x))
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

print "column.py metric="+args.metric+" out="+args.out

# with open(args.run1,'rb') as tsv1, open(args.run2, 'rb') as tsv2:


namestsv = csv.reader(open(args.names, 'r'), delimiter='\t')
# for row in namestsv:
#     print row[2][8:]
namesDict = {row[0]: row[2][8:] for row in namestsv}


def fetchValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    data = {row[0]: float(row[2]) for row in tsv if row[1] == args.metric and not math.isnan(float(row[2]))}
    return data

for run in args.runs:



    # datas = {run: fetchValues(run) for run in args.runs}

    # deal with nans
    # queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
    # basedata=datas[args.runs[0]]
    # queries = set(basedata.keys()).difference(queriesWithNanValues)


    # seriesDict = {run:dict() for run in args.runs}



    # for run in datas:
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    seriesDict = [float(row[2]) for row in tsv if row[0] in namesDict]
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    labelseriesDict = [namesDict[row[0]] for row in tsv if row[0] in namesDict]
    # seriesDict[run] = data


    df2 = DataFrame(seriesDict, index=labelseriesDict, columns=[os.path.basename(run)])
    # df2.index=[os.path.basename(label) for label in df1.index]

    # df2=df[args.runs[0]]

    plt.figure()
    df2.plot(kind='bar', color=['1.0', '0.70', '0.0', '0.50'])
    plt.ylabel(args.metric, fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=10)
    plt.xticks(rotation=90)
    plt.savefig(args.out+os.path.basename(run)+'.pdf', bbox_inches='tight')

    # plt.show()
