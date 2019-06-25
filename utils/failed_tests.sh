#!/bin/bash

logdir=$1;

for i in {1..5}
do
    grep "Result: FAIL" -3 ${logdir}/regression-$i.log | \
        grep "End of test" | awk '{print $5}';
done
