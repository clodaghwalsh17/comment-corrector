from comment_corrector.extract_comments import list_comments
from comment_corrector.semantic_diff import diff
from comment_corrector.utils import Utils
import argparse
import sys

def init_argparse():        
    parser = argparse.ArgumentParser()
    parser.add_argument("file_v1", help = "Version 1 of file to be analysed")
    parser.add_argument("file_v2", help = "Version 2 of file to be analysed")
    args = parser.parse_args()
    return args
    
def run():     
    args = init_argparse()
    files = (args.file_v1, args.file_v2)   
   
    utils = Utils()
    try:
        utils.validate_files(files)
    except Exception as e:
        print(e)  
        sys.exit()
    
    mime_type = utils.get_mime_type(args.file_v1)
    
    comments_file2 = list_comments(args.file_v2, mime_type) 
      
    if comments_file2:
        comments_file1 = list_comments(args.file_v1, mime_type)
        if comments_file1:
            edit_script = diff(files, utils.get_programming_language(args.file_v1))
            print(edit_script)
        else:
            print("New comments added")       