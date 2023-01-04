from comment_corrector.extract_comments import list_comments
import argparse

def init_argparse():        
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help = "File to be parsed")
    args = parser.parse_args()
    return args

def run():     
    args = init_argparse()
    comments = list_comments(args.file)
    print(comments)
