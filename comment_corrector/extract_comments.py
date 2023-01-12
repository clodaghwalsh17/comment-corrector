from comment_parser import comment_parser
from comment_parser.parsers.common import Comment
import sys
import re

def list_comments(file, mime):
    try:
        comments = comment_parser.extract_comments(file, mime)
        if mime == "text/x-python":
            # Comment Corrector doesn't track shebang or encoding
            for comment in comments:
                if is_shebang(comment) or is_encoding(comment):
                    comments.remove(comment)

            comments.extend(find_python_documentation_comments(file))
            
        return comments
    except Exception as e:        
        print(e)  
        sys.exit()  

def find_python_documentation_comments(file):
    with open(file) as f:
        code = f.read()

    regex = "\"{3}[ \t\n\r]*([<>%!@#'._,;:a-zA-Z0-9\+-/\*=\(\)\[\]\n ]+)\"{3}"
    regex_matches = re.findall(regex, code)
    doc_comments = []

    if regex_matches:
        for regex_match in regex_matches:
            doc_comments.append(create_comment(regex_match, 1, True)) # TODO find line number

    return doc_comments

def is_shebang(comment):
    return comment.line_number() == 1 and comment.text()[0] == "!"

def is_encoding(comment):
    txt = comment.text()
    regex = "coding[:=][ \t]*([-_.a-zA-Z0-9]+)"
    result = re.search(regex, txt)
    return comment.line_number() <= 2 and result is not None

def create_comment(comment, line_number, is_multiline):
    return Comment(comment, line_number, is_multiline)