from __future__ import print_function
from collections import defaultdict
import os
import math
import scipy

__author__ = 'dietz'

from argparse import ArgumentParser
import scipy.stats as sciStats

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

tooldescription = """
Compute paired T-test for any run against the baseline (first run).
Prints t-statistics and p-value for two-sided test.
"""
parser = ArgumentParser(description=tooldescription)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--format', help='trec_eval output or galago_eval output', default='trec_eval')
parser.add_argument('--best',  action="store_true", help="compare all to best run (default: first run)")
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))

def main():

    args = parser.parse_args()


    def read_ssv(fname):
        lines = [line.split() for line in open(fname, 'r')]
        if args.format.lower() == 'galago_eval':
            return lines
        elif args.format.lower() == 'trec_eval':
            return [[line[1], line[0]] + line[2:] for line in lines]


    def fetchValues(run):
        tsv = read_ssv(run)
        data = {row[0]: float(row[2]) for row in tsv if row[1] == args.metric}
        return data

    def findQueriesWithNanValues(run):
        tsv = read_ssv(run)
        queriesWithNan = {row[0] for row in tsv if row[1] == 'num_rel' and (float(row[2]) == 0.0 or math.isnan(float(row[2])))}
        return queriesWithNan


    datas = {run: fetchValues(run) for run in args.runs}

    queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
    firstrun=datas[args.runs[0]]
    queries = set(firstrun.keys()).difference(queriesWithNanValues)
    queriesList = list(queries)

    if args.best:
        dlist=[(d['all'], d) for key, d in datas.items()]
        basedata = max(dlist, key=lambda dup:dup[0])[1]
    else:
        basedata = firstrun

    basearray= [basedata.get(key,0) for key in queriesList]


    for run in datas:
        if not run == args.runs[0]:
            data = datas[run]

            dataarray= [data.get(key,0) for key in queriesList]

            (tstat, prob) = sciStats.ttest_rel(basearray, dataarray)
            print (run, tstat, prob)

if __name__ == '__main__':
    main()
