#!/bin/sh -l

output=$(cd / && python3 -m comment_corrector v1.py v2.py)

if [ "$output" = "" ]; then
    echo "Comment Corrector identified no comments in need of review"
    exit 0
else
    echo "::warning ::Comment Corrector identified comments in need of review"
    echo "::group::Comments to Review"
    echo "::group::v2.py"
    echo "$output"
    echo "::endgroup::"
    echo "::endgroup::"
    exit 1
fi