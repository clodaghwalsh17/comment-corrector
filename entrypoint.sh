#!/bin/sh -l

output=$(cd / && python3 -m comment_corrector /github/workspace/file_a.py /github/workspace/file_b.py -w $1)

if [ "$output" = "" ]; then
    echo "Comment Corrector identified no comments in need of review"
    exit 0
else
    echo "::warning ::Comment Corrector identified comments in need of review"
    echo "::group::v2.py"
    echo "$output"
    echo "::endgroup::"
    exit 1
fi