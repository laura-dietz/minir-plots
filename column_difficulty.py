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
import operator

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
parser.add_argument('--diffmetric', help='metric for difficulty')
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

diffmetric = args.diffmetric if args.diffmetric is not None else args.metric
# with open(args.run1,'rb') as tsv1, open(args.run2, 'rb') as tsv2:

print "column_difficulty.py metric="+args.metric+" diffmetric="+diffmetric+"  out="+args.out


def findQueriesWithNanValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    queriesWithNan = {row[0] for row in tsv if row[1] == 'num_rel' and (float(row[2])==0.0 or math.isnan(float(row[2])))}
    return queriesWithNan

def fetchValues(run, metric = args.metric):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    data = {row[0]: float(row[2]) for row in tsv if row[1] == metric and not math.isnan(float(row[2]))}
    return data


datas = {run: fetchValues(run) for run in args.runs}

# deal with nans
queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
basedata=fetchValues(args.runs[0], diffmetric)
print basedata

queries = set(basedata.keys()).difference(queriesWithNanValues)



basev = [(key, basedata[key]) for key in queries]
basev.sort(key=operator.itemgetter(1))


queriesDiff = {
    '0%-5%':basev[0:int(len(basev)*0.05)],
    '5%-25%':basev[int(len(basev)*0.05):int(len(basev)*0.25)],
    '25%-50%':basev[int(len(basev)*0.25):int(len(basev)*0.5)],
    '50%-75%':basev[int(len(basev)*0.5):int(len(basev)*0.75)],
    '75%-95%':basev[int(len(basev)*0.75):int(len(basev)*0.95)],
    '95%-100%':basev[int(len(basev)*0.95):],
}

seriesDict = {key:dict() for key in queriesDiff}


for run in datas:
    data = datas[run]

    mean = np.average([data[key] for key in queries])
    stderr = np.std([data[key] for key in queries]) / sqrt(len(queries))
    for (label, queriesByD) in queriesDiff.iteritems():
        seriesDict[label][run]=np.average([data[key] for (key, x) in queriesByD])




print "dropping queries because of NaN values: "+ " ".join(queriesWithNanValues)

# print '\t'.join(['run', 'mean/stderr'])
# for run in datas:
#     if not run == args.runs[0]:
#         print '\t'.join([run, str(seriesDict['mean'][run]), str(seriesDict['stderr'][run])])


df1 = DataFrame(seriesDict, columns=("0%-5%", "5%-25%", '25%-50%','50%-75%','75%-95%','95%-100%'), index=args.runs)
df2 = df1
df2.index=[os.path.basename(label) for label in df1.index]

df3=df2.transpose()

plt.figure()
df3.plot(kind='bar',label=args.metric, color=['1.0', '0.80', '0.4', '0.0', '0.70'])
leg = plt.legend(loc='best', fancybox=True)
leg.get_frame().set_alpha(0.5)
plt.tick_params(axis='both', which='major', labelsize=11)
plt.xticks(rotation=0)
plt.ylabel(args.metric, fontsize=20)
plt.xlabel("difficulty percentile according to "+os.path.basename(args.runs[0]), fontsize=20)


plt.savefig(args.out, bbox_inches='tight')
# plt.show()
