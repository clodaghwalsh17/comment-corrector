#!/bin/bash -l
successful_run=0
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
        echo "::error ::Comment Corrector failed on the file "$file" due to the following error:$output"
        successful_run=1
        continue
    fi

    if [ "$output" != "" ]; then
        echo "::warning ::Comment Corrector identified comments in need of review in the file "$file""
        echo "::group::"$file""
        echo "$output"
        echo "::endgroup::"
    fi

done

exit $successful_run