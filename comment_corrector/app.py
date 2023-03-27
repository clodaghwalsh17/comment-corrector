from comment_corrector.utils import Utils
from comment_corrector.python_comment_analyser import PythonCommentAnalyser
import argparse
import sys

def init_argparse():        
    parser = argparse.ArgumentParser()
    parser.add_argument("v1", help = "Version 1 of file to be analysed")
    parser.add_argument('-v2', help = "Optional version 2 of file to compare against")
    parser.add_argument('-w', '--words', type=str, help = "Optional custom words for spell checker")
    args = parser.parse_args()
    return args
    
def run():     
    args = init_argparse()
    files = [args.v1]   

    if args.v2 is not None:
        files.append(args.v2)

    try:
        Utils.validate_files(files)
    except Exception as e:
        print(e)  
        sys.exit()

    language = Utils.get_programming_language(args.v1)
    if language == "Python":
        analyser = PythonCommentAnalyser(files)
   
    if args.words != 'undefined':
        analyser.set_spellchecker_custom_words(args.words)
    
    comments = analyser.analyse_comments() 
    
    output = ""
    for comment in comments:
        output += str(comment) 

    print(output)