#!/bin/sh -l
cd /

IFS='.'

file="file_a.py"

sha=$(git log --skip=1 --max-count=1 --pretty=format:%H "$file")
file_content=$(git show $sha:"$file")
read -a strarr <<< "$file"
tmp_file="/tmp/${strarr[0]}_prev.${strarr[1]}"
touch "$tmp_file"
echo $file_content >> "$tmp_file"

output=$(python3 -m comment_corrector "$file" "$tmp_file" -w $1)

if [ "$output" = "" ]; then
    echo "Comment Corrector identified no comments in need of review"
else
    echo "::warning ::Comment Corrector identified comments in need of review"
    echo "::group::"$file""
    echo "$output"
    echo "::endgroup::"
fi

exit 0