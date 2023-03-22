#!/bin/sh -l

output=$(cd / && python3 -m comment_corrector /github/workspace/file_a.py /github/workspace/ea55e3b5ce8794add6ba14d6933da320dd860dae/file_b.py -w $1)

if [ "$output" = "" ]; then
    echo "Comment Corrector identified no comments in need of review"
    exit 0
else
    echo "::warning ::Comment Corrector identified comments in need of review"
    echo "$output"
    exit 1
fi