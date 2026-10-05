#!/bin/bash
# usage: ./report.sh access.log
# Laboratory 3 - Part 5 Log Summary Script

log=$1
if [ ! -f "$log" ]; then
  echo "no such file: $log" >&2
  exit 1
fi

total=$(wc -l < "$log")
fails=$(grep -c FAIL "$log")
echo "$total requests, $fails failed"

# Completed TODO: iterate over user0 through user6 and report individual failure totals
for u in {0..6}; do
  u_fails=$(grep "user$u " "$log" | grep -c FAIL)
  echo "user$u: $u_fails failures"
done
