from __future__ import print_function
from collections import defaultdict
import csv
import os
import math

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
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--delta', help='Minimum difference to be considered', type=float, default=0.00)
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))
args = parser.parse_args()

# with open(args.run1,'rb') as tsv1, open(args.run2, 'rb') as tsv2:

def fetchValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    data = {row[0]: float(row[2]) for row in tsv if row[1] == args.metric}
    return data

def findQueriesWithNanValues(run):
    tsv = csv.reader(open(run, 'r'), delimiter='\t')
    queriesWithNan = {row[0] for row in tsv if row[1] == 'num_rel' and (float(row[2]) == 0.0 or math.isnan(float(row[2])))}
    return queriesWithNan


datas = {run: fetchValues(run) for run in args.runs}

queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
basedata=datas[args.runs[0]]
queries = set(basedata.keys()).difference(queriesWithNanValues)

basedata = datas[args.runs[0]]
helpsDict = defaultdict(list)
hurtsDict = defaultdict(list)

for run in datas:
    if not run == args.runs[0]:
        data = datas[run]
        helps = list()
        hurts = list()
        for key in queries:
            baseValue = basedata[key]
            value = data[key]
            if value - args.delta > baseValue:
                helps.append(key)
            if value + args.delta < baseValue:
                hurts.append(key)

        helpsDict[run] = helps
        hurtsDict[run] = hurts

print ('\t'.join(['run', 'num helps', 'num hurts', 'list helps', 'list hurts']))
for run in datas:
    if not run == args.runs[0]:
        print ('\t'.join([run, str(len(helpsDict[run])), str(len(hurtsDict[run])), ' '.join(helpsDict[run]),
                         ' '.join(hurtsDict[run])]))

# prefix = '/home/dietz/kbbridge/writing/sigir2014/data/eval/clueweb09b/'
# EQFE_help = set(helpsDict[prefix+'EQFE'])
# EQFE_help.difference_update(set(helpsDict[prefix+'rm']))
# EQFE_help.difference_update(set(helpsDict[prefix+'wikiRm1']))
#
# for q in EQFE_help:
#     print (q,'EQFE',datas[prefix+'EQFE'][q],'SDM',basedata[q])