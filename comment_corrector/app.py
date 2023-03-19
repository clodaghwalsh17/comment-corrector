from comment_corrector.utils import Utils
from comment_corrector.python_comment_analyser import PythonCommentAnalyser
import argparse
import sys
import os

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

    try:
        Utils.validate_files(files)
    except Exception as e:
        print(e)  
        sys.exit()

    language = Utils.get_programming_language(args.file_v1)
    if language == "Python":
        analyser = PythonCommentAnalyser(files)
   
    if args.language != 'undefined' and args.words != 'undefined':
        print("Setting both")
        analyser.set_spellchecker_settings(args.language, args.words)
    elif args.language != 'undefined':
        print("Setting language")
        analyser.set_spellchecker_language(args.language)
    elif args.words != 'undefined':
        print("Setting custom words")
        analyser.set_spellchecker_custom_words(args.words)
    
    comments = analyser.analyse_comments() 
    for comment in comments:
        print(comment)   