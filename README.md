minir-plots
===========

Mini Plotting scripts for IR experiments.

Works with query-by-query output of trec-eval and galago-eval evaluation code which produce run files in the tab-separated form queryId, metric, value.

Example:

    queryId metric value
    C09-1	ndcg	0.27478
    C09-1	ndcg5	0.47244
    C09-1	ndcg10	0.32972
    C09-1	ndcg20	0.25703
    C09-1	ERR	0.18652
    C09-1	ERR10	0.16907
    C09-1	ERR20	0.17581
    C09-1	P1	1.00000
    C09-2	ndcg	0.25
    C09-2	ndcg5	0.37244
    C09-2	ndcg10	0.22972
    C09-2	ndcg20	0.26703
    C09-2	ERR	0.19652
    C09-2	ERR10	0.17907
    C09-2	ERR20	0.18581
    C09-2	P1	0.0

These scripts require Python 3, numpy, scipy, matplotlib and pandas.

Install
-------

Option A) setup.py:

1. `python setup.py install`. 
2. Call scripts `python column.py  ...`

Option B) Nix:

1. Install NIX from <https://nixos.org/nix/>
2. cd into minir-plots; run `nix build`
3. Call scripts with `nix run -f $minirPlotsDirectory -c $minirScript ...`

where `$minirPlots` is the directory into which you checked out this repository and `$minirScript` is one of the plotting options listed below.

For other scripts (other than column.py/minir-column) see documentation below.



Creating column plots with std error bars
-------------------------------------------

Classic bar chart indicating the mean of values for the given metric across all queries with error bars indicating the standard error.

```
usage: nix run -f $minirPlotsDirectory -c minir-column  [-h] --out FILE --metric METRIC runs [runs ...]

or: python column.py [-h] --out FILE --metric METRIC [-c] [-s] runs [runs ...]

positional arguments:
  runs

optional arguments:
  -h, --help       show this help message and exit
  --out OUT        outputfilename
  --metric METRIC  metric for comparison
  -c               also include omitted queries with score 0 (requires "num_q" entry)
  --sort           sorts runs by performance
  
```


Creating column plots grouped in columns by difficulty
------------------------------------------------------

Unconventional bar chart showing the mean performance for queries of different difficulties. Difficulty is defined by
the performance of the first run (baseline). The chart contains a group for the 5% most difficult queries to the left,
5% easiest queries (to the right) as well as quartiles and intermediate ranges.

```
usage: nix run -f $minirPlotsDirectory -c minir-column-difficulty  [-h]  --out FILE --metric METRIC
                                   [--diffmetric DIFFMETRIC]
                                   baselinerun [runs ...]

or: python column_difficulty.py [-h] ... (as above)

positional arguments:
  baselinerun           run file to define difficulty of queries
  runs                  other run file for comparison

optional arguments:
  -h, --help            show this help message and exit
  --out OUT             outputfilename
  --metric METRIC       metric for comparison
  --diffmetric DIFFMETRIC
                        metric for difficulty

```

If the diffmetric is given, the queries will be divided into difficulty according to how the baseline run performs on
the diffmetric, the columns will indicate the performance under the given metric.



Hurts-helps analysis
---------------------
Using the first run as the baseline, computes the numbers of queries on which each run improved performance ("helps")
or lowered the performance ("hurt"). Also lists the queries that were helped or hurts separated by spaces.

```
usage: nix run -f $minirPlotsDirectory -c minir-hurtshelps [-h] --metric METRIC [--delta DELTA] runs [runs ...]
or: python hurtshelps.py [-h] --metric METRIC [--delta DELTA] runs [runs ...]

positional arguments:
  runs

optional arguments:
  -h, --help       show this help message and exit
  --metric METRIC  metric for comparison
  --delta DELTA    Minimum difference to be considered
```

If delta is given, only queries that differed by at least this amout are considered in the analysis.

Paired T-test
-------------

Compute paired T-test for any run against the baseline (first run). Prints t-statistics and p-value for two-sided test.

```
usage: nix run -f $minirPlotsDirectory -c minir-pairttest [-h] --metric METRIC runs [runs ...]
or: python paired-ttest.py [-h] --metric METRIC baselinerun [runs ...]

positional arguments:
  baselinerun      run file to define difficulty of queries
  runs             other runs to compare

optional arguments:
  -h, --help       show this help message and exit
  --metric METRIC  metric for comparison
```
