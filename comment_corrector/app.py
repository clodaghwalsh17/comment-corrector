from comment_corrector.utils import Utils
from comment_corrector.python_comment_analyser import PythonCommentAnalyser
import argparse
import sys
import os

def init_argparse():        
    parser = argparse.ArgumentParser()
    parser.add_argument("file_v1", help = "Version 1 of file to be analysed")
    parser.add_argument("file_v2", help = "Version 2 of file to be analysed")
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

    language = os.environ.get('INPUT_SPELLCHECKER-LANGUAGE')
    words = os.environ.get('INPUT_CUSTOM-WORDS-FILE')
    
    if language and words:
        analyser.set_spellchecker_settings(language, words)
    elif language:
        analyser.set_spellchecker_language(language)
    elif words:
        analyser.set_spellchecker_custom_words(words)
    
    comments = analyser.analyse_comments() 
    for comment in comments:
        print(comment)   