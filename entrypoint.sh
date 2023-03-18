#!/bin/sh -l

output=$(cd / && python3 -m comment_corrector v1.py v2.py)

echo $output
if [ "$output" = "" ]; then
    echo "No errors found"
    exit 0
else
    echo "::warning ::Comment Corrector marked the following comments as in need of review"
    echo "::group::Comments to Review"
    echo "Comment 1"
    echo "::endgroup::"
    exit 1
fi