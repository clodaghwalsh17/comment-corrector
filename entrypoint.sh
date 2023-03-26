#!/bin/bash -l
files=$(cd / && python3 retrieve_files.py)

for file in ${files[@]}; 
do
    echo "$file"
    current_file="/github/workspace/$file"

    sha=$(cd /github/workspace && git log --skip=1 --max-count=1 --pretty=format:%H "$file")
    # TODO check that sha is not empty
    file_content=$(git show $sha:"$file")
    # TODO account for case where file inside a folder
    tmp_file="/tmp/$file" 
    touch "$tmp_file"
    echo "$file_content" >> "$tmp_file"

    output=$(cd / && python3 -m comment_corrector "$tmp_file" "$current_file" -w "$1")

    # TODO check if exit code of comment corrector is not zero
    if [ "$output" = "" ]; then
        echo "Comment Corrector identified no comments in need of review"
    else
        echo "::warning ::Comment Corrector identified comments in need of review"
        echo "::group::"$file""
        echo "$output"
        echo "::endgroup::"
    fi
done

exit 0