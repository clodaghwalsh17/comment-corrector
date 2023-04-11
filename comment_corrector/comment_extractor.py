from comment_parser import comment_parser
from comment_corrector.comment import Comment
from comment_corrector.category import Category
from comment_corrector.utils import Utils
from comment_corrector.docstring_extractor import DocstringExtractor
import sys
import re

class CommentExtractor():

    def __init__(self, mime_type):
        self.__mime_type = mime_type

    def extract_comments(self, file):
        try:
            comments = [Comment.from_comment_parser(comment) for comment in comment_parser.extract_comments(file, self.__mime_type)]
            
            if self.__mime_type == "text/x-python":                         
                comments = self.__process_python_comments(file, comments)
                
                docstring_extractor = DocstringExtractor(file)
                docstrings = docstring_extractor.extract_docstrings()
                if docstrings:
                    comments.extend(docstrings)
                    comments.sort(key=Utils.sort_comments)
            
            return comments
        except Exception as e:   
            print("The following error occurred while extracting comments from the input file: {}".format(e))    
            sys.exit(1)  

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
        
        comment_list.sort(key=Utils.sort_comments) 
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

    def __remove_unwanted_comment(self, comment_list, text):
        comment_list = [comment for comment in comment_list if comment.text() != text.strip()[1:].strip()]
        return comment_list