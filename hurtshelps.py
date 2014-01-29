import csv
import os

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
       parser.error("The file %s does not exist!"%arg)
    else:
       return open(arg,'r')  #return an open file handle

parser = ArgumentParser()
parser.add_argument('--run1', metavar="FILE", dest='run1', required=True, type=lambda x: is_valid_file(parser,x))
parser.add_argument('--run2', metavar="FILE", dest='run2', required=True, type=lambda x: is_valid_file(parser,x))
parser.add_argument('--metric', help='metric for comparison', required=True)
parser.add_argument('--delta', help='Minimum difference to be considered', type=float, default=0.00)
args = parser.parse_args()

# with open(args.run1,'rb') as tsv1, open(args.run2, 'rb') as tsv2:
tsv1 = csv.reader(args.run1, delimiter='\t')

tsv2 = csv.reader(args.run2, delimiter='\t')

data1 = {row[0]: float(row[2]) for row in tsv1 if row[1] == args.metric}
data2 = {row[0]: float(row[2]) for row in tsv2 if row[1] == args.metric}

helps=list()
hurts=list()

for key in data1:
    value1 = data1[key]
    value2 = data2[key]
    if value1 > value2 + args.delta:
        helps.append(key)
    if value1 < value2 - args.delta:
        hurts.append(key)

print 'helps\t',len(helps)
print 'hurts\t',len(hurts)

print 'helps for queries:', ' '.join(helps)
print 'hurts for queries:', ' '.join(hurts)
