#!/bin/bash -l
files=$(cd / && python3 retrieve_files.py)

for file in ${files[@]}; 
do
    workspace_file="/github/workspace/$file"

    sha=$(cd /github/workspace && git log --skip=1 --max-count=1 --pretty=format:%H "$file")

    if [ "$sha" != "" ]; then
        file_content=$(git show $sha:"$file")

        tmp_filename=$(awk -F/ '{print $NF}' <<< "$file")
        tmp_file="/tmp/$tmp_filename" 
        touch "$tmp_file"
        echo "$file_content" >> "$tmp_file"
        
        output=$(cd / && python3 -m comment_corrector "$tmp_file" -v2 "$workspace_file" -w "$1")
        rm "$tmp_file"
    else
        output=$(cd / && python3 -m comment_corrector "$workspace_file" -w "$1")
    fi    

    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "::error ::Comment Corrector failed on the file "$file" due to the following error.\n$output"
        exit 1
    fi

    if [ "$output" = "" ]; then
        echo "Comment Corrector identified no comments in need of review"
    else
        echo "::warning ::Comment Corrector identified comments in need of review in the file "$file""
        echo "::group::"$file""
        echo "$output"
        echo "::endgroup::"
    fi

done

exit 0