from comment_parser import comment_parser
import sys

def list_comments(file, mime):
    try:
        comments = comment_parser.extract_comments(file, mime)
        return comments
    except Exception as e:        
        print(e)  
        sys.exit()     