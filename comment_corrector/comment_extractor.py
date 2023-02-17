from comment_parser import comment_parser
from comment_corrector.comment import Comment
from comment_corrector.category import Category
import sys
import re

class CommentExtractor():

    DOC_COMMENT_KEYWORDS = ["parameter", "parameters", "param", "params", "return", "returns", \
    "input", "output", "type", "argument", "arguments", "arg", "args", "kwargs", "accepts", "function", "call"]

    def __init__(self, mime_type):
        self.__mime_type = mime_type

    def extract_comments(self, file):
        try:
            comments = [Comment.from_comment_parser(comment) for comment in comment_parser.extract_comments(file, self.__mime_type)]
            
            if self.__mime_type == "text/x-python":                         
                comments = self.__process_python_comments(file, comments)
                
                try:
                    doc_comments = self.__find_python_documentation_comments(file)
                    if doc_comments:
                        comments.extend(doc_comments)
                        comments.sort(key=self.__line_number_sort) 
                except Exception as e:        
                    print(e)  
                    sys.exit() 
            
            return comments
        except Exception as e:        
            print(e)  
            sys.exit()  

    def __find_python_documentation_comments(self, file):
        single_quote_pattern = "'{3}[ \t\n\r]*([<>%!@#%^&?/¬~|\\\\`'._,;:a-zA-Z0-9\+-/\*=\(\)\[\]\{\}\n ]+)'{3}" 
        double_quote_pattern = "\"{3}[ \t\n\r]*([<>%!@#%^&?/¬~|\\\\`'._,;:a-zA-Z0-9\+-/\*=\(\)\[\]\{\}\n ]+)\"{3}" 
        
        single_quote_doc_comments = self.__match_documentation_comments(file, re.compile(single_quote_pattern))
        double_quote_doc_comments = self.__match_documentation_comments(file, re.compile(double_quote_pattern))

        if single_quote_doc_comments and double_quote_doc_comments:
            raise Exception("Comment Corrector does not support files with inconsistent Python documentation comments. Please review this as it is bad practice.")
        elif single_quote_doc_comments:
            return single_quote_doc_comments
        elif double_quote_doc_comments:
            return double_quote_doc_comments

    def __match_documentation_comments(self, file, match):
        doc_comments = []
        with open(file) as f:
            code = f.read()

        end='.*\n'
        line = []
        for iter in re.finditer(end, code):
            line.append(iter.end())
        for iter in re.finditer(match, code):
            string = iter.group(1)

            is_doc_comment = False
            for keyword in self.DOC_COMMENT_KEYWORDS:
                is_doc_comment = is_doc_comment or keyword in string or keyword.capitalize() in string
            
            if is_doc_comment:
                line_number = next(i for i in range(len(line)) if line[i] > iter.start(1))
                doc_comments.append(Comment(string, line_number, True, category=Category.DOCUMENTATION))            
    
        return doc_comments

    def __process_python_comments(self, file, comment_list):
        # Group multiline comments and remove any untrackable items including shebang and encoding
        start_line = 0
        end_line = 0
        line_number = 0
        comment = ''
        comment_length = 0

        with open(file) as f:
            while True:
                line = f.readline()
                line_number += 1

                if not line:
                    # Catch any comments at the end of the file
                    if comment and start_line != end_line:
                        comment_list.append(Comment(comment, start_line, True, real_length=comment_length))
                    elif comment:
                        comment_list.append(Comment(comment, start_line, False, real_length=comment_length))
                    break  
        
                if comment and self.__is_trackable_comment(line, line_number):
                    end_line += 1
                    comment_length += len(line)
                    comment += line.strip()[1:]
                    comment_list = self.__remove_unwanted_comment(comment_list, line)
                elif self.__is_trackable_comment(line, line_number):
                    start_line = line_number
                    end_line = line_number
                    comment_length += len(line)
                    comment += line.strip()[1:]
                    comment_list = self.__remove_unwanted_comment(comment_list, line)
                elif self.__is_untrackable_comment(line, line_number):
                    comment_list = self.__remove_unwanted_comment(comment_list, line)
                    comment_list.append(Comment(line, line_number, False, real_length=len(line), category=Category.UNTRACKABLE))
                elif comment and start_line != end_line:
                    comment_list.append(Comment(comment, start_line, True, real_length=comment_length))
                    comment = ''
                    comment_length = 0
                elif comment:
                    comment_list.append(Comment(comment, start_line, False, real_length=comment_length))
                    comment = ''
                    comment_length = 0
        
        comment_list.sort(key=self.__line_number_sort) 
        return comment_list

    def __is_trackable_comment(self, string, line_number):
        # Comment Corrector doesn't track shebang or encoding
        return string.strip().startswith('#') and not self.__is_shebang(string, line_number) and not self.__is_encoding(string, line_number)

    def __is_untrackable_comment(self, string, line_number):
        return string.strip().startswith('#') and (self.__is_shebang(string, line_number) or self.__is_encoding(string, line_number))

    def __is_shebang(self, string, line_number):
        return line_number == 1 and string.startswith('#!')

    def __is_encoding(self, string, line_number):
        regex = "coding[:=][ \t]*([-_.a-zA-Z0-9]+)"
        result = re.search(regex, string)
        return line_number <= 2 and result is not None

    def __line_number_sort(self, comment):
        return comment.line_number()

    def __remove_unwanted_comment(self, comment_list, text):
        comment_list = [comment for comment in comment_list if comment.text() != text.strip()[1:].strip()]
        return comment_list