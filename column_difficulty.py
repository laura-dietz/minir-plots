from __future__ import print_function
from math import sqrt
import os

import matplotlib as mpl

import numpy as np
import math
from pandas.util.testing import DataFrame
import operator

import matplotlib.pyplot as plt


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
Unconventional bar chart showing the mean performance for queries of different difficulties.
Difficulty is defined by the performance of the first run (baseline). The chart contains a
group for the 5% most difficult queries to the left, 5% easiest queries (to the right) as well
as quartiles and intermediate ranges..
"""
parser = ArgumentParser(description=tooldescription)
parser.add_argument('--out', help='outputfilename', metavar='FILE', required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--diffmetric', help='metric for difficulty')
parser.add_argument('--format', help='trec_eval output or galago_eval output', default='trec_eval')
parser.add_argument('-c', help='instead of average, also count non-existing queries', default=False, action='store_true')
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))

def main():
    mpl.use("Agg")
    args = parser.parse_args()

    diffmetric = args.diffmetric if args.diffmetric is not None else args.metric
    numQueries_key = "num_q"

    print ("column_difficulty.py metric=" + args.metric + " diffmetric=" + diffmetric + "  out=" + args.out)


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
        queriesWithNan = {row[0] for row in tsv if
                          row[1] == 'num_rel' and (float(row[2]) == 0.0 or math.isnan(float(row[2])))}
        return queriesWithNan


    def fetchValues(run, metric=args.metric):
        tsv = read_ssv(run)
        data = {row[0]: float(row[2]) for row in tsv if row[1] == metric and not math.isnan(float(row[2]))}
        return data


    datas = {run: fetchValues(run) for run in args.runs}

    # deal with nans
    queriesWithNanValues = {'all'}.union(*[findQueriesWithNanValues(run) for run in args.runs])
    basedata = fetchValues(args.runs[0], diffmetric)
    print (basedata)

    queries = set(basedata.keys()).difference(queriesWithNanValues)
    numQueries = readNumQueries(args.runs[0]) if args.c else len(queries)

    basev = [(key, basedata[key]) for key in queries]
    basev.sort(key=operator.itemgetter(1))

    queriesDiff = {
        '0%-5%': basev[0:int(len(basev) * 0.05)],
        '5%-25%': basev[int(len(basev) * 0.05):int(len(basev) * 0.25)],
        '25%-50%': basev[int(len(basev) * 0.25):int(len(basev) * 0.5)],
        '50%-75%': basev[int(len(basev) * 0.5):int(len(basev) * 0.75)],
        '75%-95%': basev[int(len(basev) * 0.75):int(len(basev) * 0.95)],
        '95%-100%': basev[int(len(basev) * 0.95):],
    }

    seriesDict = {key: dict() for key in queriesDiff}

    for run in datas:
        data = datas[run]

        mean = np.sum([data.get(key, 0.0) for key in queries]) / numQueries
        stderr = np.std([data.get(key, 0.0) for key in queries] + ([0.0]* (numQueries - len(queries)))) / sqrt(numQueries)
        for (label, queriesByD) in queriesDiff.items():
            seriesDict[label][run] = np.average([data[key] for (key, x) in queriesByD])

    print ("dropping queries because of NaN values: " + " ".join(queriesWithNanValues))

    df1 = DataFrame(seriesDict, columns=("0%-5%", "5%-25%", '25%-50%', '50%-75%', '75%-95%', '95%-100%'), index=args.runs)
    df2 = df1
    df2.index = [os.path.basename(label) for label in df1.index]

    df3 = df2.transpose()

    bwcolors = ['0.0', '0.80', '0.4', '0.2', '0.70']
    colors = ['black', 'olivedrab', 'red',
             'indigo','hotpink','darkorchid',
             'mediumspringgreen','green','teal',
             'tomato',
             'black','slategrey',
             'navy','royalblue','deepskyblue' ]

    plt.figure( )
    df3.plot(kind='bar', label=args.metric, color=colors, figsize=(7,7), width=0.75)
    leg = plt.legend(loc='best', fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.tick_params(axis='both', which='major', labelsize=11)
    plt.xticks(rotation=0)
    plt.ylabel(args.metric, fontsize=20)
    plt.xlabel("difficulty percentile according to " + os.path.basename(args.runs[0]), fontsize=20)

    plt.savefig(args.out, bbox_inches='tight')
    # plt.show()

if __name__ == '__main__':
    main()


