from comment_corrector.semantic_diff import diff, source_to_tree
from comment_corrector.utils import Utils
from comment_corrector.python_comment_analyser import PythonCommentAnalyser
import argparse
import sys

def init_argparse():        
    parser = argparse.ArgumentParser()
    parser.add_argument("file_v1", help = "Version 1 of file to be analysed")
    parser.add_argument("file_v2", help = "Version 2 of file to be analysed")
    parser.add_argument('-l', '--language', type=str, help = "Optional language for spell checker")
    parser.add_argument('-w', '--words', type=str, help = "Optional custom words for spell checker")
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
    if mime_type == "text/x-python":
        tree = source_to_tree(args.file_v1)
        analyser = PythonCommentAnalyser(files, tree)
    
    if args.language and args.words:
        analyser.set_spellchecker_settings(args.language, args.words)
    elif args.language:
        analyser.set_spellchecker_language(args.language)
    elif args.words:
        analyser.set_spellchecker_custom_words(args.words)
    
    comments = analyser.analyse_comments() 
    print(comments)       