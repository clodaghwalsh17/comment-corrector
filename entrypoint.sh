#!/bin/sh -l
echo "$1"
echo "$2"

echo "$(ls /github/workspace/.github/workflows)"

output=$(cd / && python3 -m comment_corrector /github/workspace/file_a.py /github/workspace/file_b.py)

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