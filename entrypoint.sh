#!/bin/sh -l

output=$(python3 -m comment_corrector v1.py v2.py)

echo $output
if [ "$output" = "" ]; then
    echo "No errors found"
    exit 0
else
    echo "::warning ::Comment Corrector marked the following comments as in need of review"
    exit 1
fi