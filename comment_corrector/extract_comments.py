from comment_parser import comment_parser
from comment_parser.parsers.common import Comment
from itertools import groupby
from operator import itemgetter
import sys
import re

def list_comments(file, mime):
    try:
        comments = comment_parser.extract_comments(file, mime)
        if mime == "text/x-python":
            # Comment Corrector doesn't track shebang or encoding
            comments = [comment for comment in comments if not is_shebang(comment) and not is_encoding(comment)]
            
            comments = group_multiline_comments(comments)
            
            doc_comments = find_python_documentation_comments(file)
            if doc_comments:
                comments.extend(doc_comments)
                comments.sort(key=line_number_sort)
            
        return comments
    except Exception as e:        
        print(e)  
        sys.exit()  

def find_python_documentation_comments(file):
    doc_comments = []
    with open(file) as f:
        code = f.read()

    end='.*\n'
    line = []
    for iter in re.finditer(end, code):
        line.append(iter.end())

    pattern = "\"{3}[ \t\n\r]*([<>%!@#'._,;:a-zA-Z0-9\+-/\*=\(\)\[\]\n ]+)\"{3}"
    match = re.compile(pattern)
    for iter in re.finditer(match, code):
        line_number = next(i for i in range(len(line)) if line[i] > iter.start(1))
        doc_comments.append(create_comment(iter.group(1), line_number, True))
  
    return doc_comments

def group_multiline_comments(comment_list): 
    comments = []
    comment_line_numbers = [comment.line_number() for comment in comment_list]
    consecutive_numbers_range = []
    for k, g in groupby(enumerate(comment_line_numbers), lambda x: x[0]-x[1]):
        consecutive_numbers_range.append(list(map(itemgetter(0), g)))
    
    for range in consecutive_numbers_range: 
        if len(range) == 1:
            # Single line comment
            comments.append(comment_list[range[0]])
        else:
            # Multiline comment
            start_line = comment_list[range[0]].line_number()
            comment_fragments = [comment_list[i].text() for i in range]           
            comment = ''.join(comment_fragments)
            comments.append(create_comment(comment, start_line, True))
    
    return comments

def is_shebang(comment):
    return comment.line_number() == 1 and comment.text()[0] == "!"

def is_encoding(comment):
    txt = comment.text()
    regex = "coding[:=][ \t]*([-_.a-zA-Z0-9]+)"
    result = re.search(regex, txt)
    return comment.line_number() <= 2 and result is not None

def line_number_sort(comment):
    return comment.line_number()

def create_comment(comment, line_number, is_multiline):
    return Comment(comment, line_number, is_multiline)