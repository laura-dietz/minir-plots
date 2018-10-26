from __future__ import print_function
import csv
import os
from pandas.util.testing import DataFrame
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


parser = ArgumentParser()
parser.add_argument('--out', help='outputfilename', required=True)
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--names', help='filename for names lookup', required=True, type=lambda x: is_valid_file(parser, x))
parser.add_argument('--format', help='trec_eval output or galago_eval output', default='trec_eval')
parser.add_argument(dest='runs', nargs='+', type=lambda x: is_valid_file(parser, x))

def main():

    args = parser.parse_args()

    print ("feature-column.py metric=" + args.metric + " out=" + args.out)


    def read_ssv(fname):
        lines = [line.split() for line in open(fname, 'r')]
        if args.format.lower() == 'galago_eval':
            return lines
        elif args.format.lower() == 'trec_eval':
            return [[line[1], line[0]] + line[2:] for line in lines]



    namestsv = read_ssv(args.names)
    namesDict = {row[0]: row[2][8:] for row in namestsv}

    for run in args.runs:
        tsv =read_ssv(run)
        values = [float(row[2]) for row in tsv if row[0] in namesDict]
        tsv = read_ssv(run)
        labels = [namesDict[row[0]] for row in tsv if row[0] in namesDict]

        df2 = DataFrame(values, index=labels, columns=[os.path.basename(run)])

        plt.figure()
        df2.plot(kind='bar', color=['1.0', '0.70', '0.0', '0.50'])
        plt.ylabel(args.metric, fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.xticks(rotation=90)
        plt.savefig(args.out + os.path.basename(run) + '.pdf', bbox_inches='tight')

        # plt.show()


if __name__ == '__main__':
    main()