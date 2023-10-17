#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

cd ~/projects/neosca-pytregex
python -m neosca ~/docx/corpus/treebank/combined/*.mrg --no-parse -m -o /tmp/after_to_sort.csv
sort /tmp/after_to_sort.csv > /tmp/after.csv
cd ~/projects/neosca
python -m neosca ~/docx/corpus/treebank/combined/*.mrg --no-parse -m -o /tmp/before_to_sort.csv
sort /tmp/before_to_sort.csv > /tmp/before.csv

paste -d '\n' <(diff -u /tmp/before.csv /tmp/after.csv | grep -E '^\+[^+]' | sort) <(diff -u /tmp/before.csv /tmp/after.csv | grep -E '^-[^-]' | sort) | sed -E 's/^[+-]//' > /tmp/diff-pytregex.csv
awk -F, 'BEGIN {split("Filename,W,S,VP,C,T,DC,CT,CP,CN,MLS,MLT,MLC,C/S,VP/T,C/T,DC/C,DC/T,T/S,CT/T,CP/T,CP/C,CN/T,CN/C", header, ",")}; (NR % 2 != 0) {for (i=1; i<=NF; i++) {arr[i]=$i}}; (NR % 2 == 0) {for (i=1; i<=NF; i++) {if ($i != arr[i] && match(header[i], "/|ML") == 0) {print $1,header[i],arr[i],$i}}}' /tmp/diff-pytregex.csv > /tmp/diff-pytregex.txt
nvim /tmp/diff-pytregex.txt
