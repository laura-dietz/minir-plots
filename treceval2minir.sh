#!/bin/bash

# converts pretty-space formatted treceval and galagoeval format into tab-separated format - to be used as inputs for minir-plots

awk -v OFS="\t" ' { print $2, $1 ,$3; } ' $1