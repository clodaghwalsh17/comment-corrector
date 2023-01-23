from comment_parser import comment_parser
from comment_corrector.comment import Comment
from itertools import groupby
from operator import itemgetter
import sys
import re

DOC_COMMENT_KEYWORDS = ["parameter", "parameters", "param", "params", "return", "returns", \
"input", "output", "type", "argument", "arguments", "arg", "args", "kwargs", "accepts", "function", "call"]

def list_comments(file, mime):
    try:
        comments = [Comment(comment.text(), comment.line_number(), comment.is_multiline()) for comment in comment_parser.extract_comments(file, mime)]
        
        if mime == "text/x-python":                   
            # Comment Corrector doesn't track shebang or encoding
            comments = [comment for comment in comments if not __is_shebang(comment) and not __is_encoding(comment)]
            
            comments = __group_multiline_comments(comments)
            
            doc_comments = __find_python_documentation_comments(file)
            if doc_comments:
                comments.extend(doc_comments)
                comments.sort(key=line_number_sort) 
            
        return comments
    except Exception as e:        
        print(e)  
        sys.exit()  

def __find_python_documentation_comments(file):
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
        string = iter.group(1)

        is_doc_comment = False
        for keyword in DOC_COMMENT_KEYWORDS:
            is_doc_comment = is_doc_comment or keyword in string or keyword.capitalize() in string
        
        if is_doc_comment:
            line_number = next(i for i in range(len(line)) if line[i] > iter.start(1))
            doc_comments.append(Comment(string, line_number, True))            
  
    return doc_comments

def __group_multiline_comments(comment_list): 
    comments = []
    comment_line_numbers = [comment.line_number() for comment in comment_list]
    consecutive_numbers_range = []
    for k, g in groupby(enumerate(comment_line_numbers), lambda x: x[0]-x[1]):
        consecutive_numbers_range.append(list(map(itemgetter(0), g)))
    
    for range in consecutive_numbers_range: 
        if len(range) == 1:
            # Single line comment
            comment = comment_list[range[0]]
            comments.append(Comment(comment.text(), comment.line_number(), comment.is_multiline()))
        else:
            # Multiline comment
            start_line = comment_list[range[0]].line_number()
            comment_fragments = [comment_list[i].text() for i in range]           
            comment = ''.join(comment_fragments)
            comments.append(Comment(comment, start_line, True))
    
    return comments

def __is_shebang(comment):
    return comment.line_number() == 1 and comment.text()[0] == "!"

def __is_encoding(comment):
    txt = comment.text()
    regex = "coding[:=][ \t]*([-_.a-zA-Z0-9]+)"
    result = re.search(regex, txt)
    return comment.line_number() <= 2 and result is not None

def __line_number_sort(comment):
    return comment.line_number()
