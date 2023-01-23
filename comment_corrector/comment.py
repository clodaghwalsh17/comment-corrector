# https://realpython.com/python-getter-setter/
# Need to check comment type is only one of select few
# how to set new attributes like type and status afterwards ??? just set new attribute with self.xxx
# Mulit constructors by using the optional arg
# https://realpython.com/python-multiple-constructors/
class Comment():

    def __init__(self, text, line_number, is_multiline, category=""):
        self.__text = text
        self.__line_number = line_number
        self.__is_multiline = is_multiline
        self.__category = category

    # line number text multiline
    # line number text multiline plus category??
    # using comment_parser comment
    # comment_parser comment plus category

    @classmethod
    def from_comment_parser(base_comment, category=""): # have an optional param here for category default is empty
        return cls(base_comment.text(), base_comment.line_number(), base_comment.is_multiline(), category)

    def calc_comment_length(self):
        return len(self.__text())
    
    # Q ?
    def categorise_comment(self, category):
        self.__category = category
    
    def category(self): # might be null
        return self.__category
    
    # Q ? 
    def update_status(self, status):
        self.__status = status

    def comment_status(self):
        return self.__status

    def text(self):
        return self.__text
    
    def line_number(self):
        return self.__line_number
    
    def is_multiline(self):
        return self.__is_multiline
    
    def __str__(self):
        return self.__text

    def __repr__(self):
        return 'Comment(%s, %s, %s, %s)' % (self.__text, self.__line_number, self.__is_multiline, self.__category)  