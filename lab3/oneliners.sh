#!/bin/bash
# Lab 3, Part 4 - one-liners. Run inside ~/os-lab3: bash oneliners.sh
# Each line of access.log: date time user result page

# Q1. How many requests failed?
echo '--- Q1'
grep -c FAIL access.log

# Q2. How many different pages were requested, and which?
echo '--- Q2'
cut -d' ' -f5 access.log | sort -u | awk '{print} END{print NR " different pages"}'

# Q3. How many requests did each page get?
echo '--- Q3'
cut -d' ' -f5 access.log | sort | uniq -c

# Q4. Which user or users have the most failed requests, and how many?
echo '--- Q4'
grep FAIL access.log | cut -d' ' -f3 | sort | uniq -c | sort -rn | awk 'NR==1{max=$1} $1==max'

# Q5. How many requests did user3 make, and how many of them failed?
echo '--- Q5'
echo "user3: $(grep -cw user3 access.log) requests, $(grep -w user3 access.log | grep -c FAIL) failed"

# Q6. Print the last 3 failed requests, showing only time and user.
echo '--- Q6'
grep FAIL access.log | tail -n 3 | cut -d' ' -f2,3

# Q7. Which login shells appear in /etc/passwd, and how many accounts use each? (field 7, separator :)
echo '--- Q7'
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn

# Q8. PREDICT, then explain: why do ls /etc | wc -l and ls -l /etc | wc -l differ by exactly one?
echo '--- Q8'
ls /etc | wc -l ; ls -l /etc | wc -l ; ls -l /etc | head -1

# Bonus (+1). Minute ends in 0 and the request failed (lines, then count).
echo '--- Bonus'
grep -E '^[^ ]+ 10:[0-5]0 [^ ]+ FAIL ' access.log ; grep -cE '^[^ ]+ 10:[0-5]0 [^ ]+ FAIL ' access.log
