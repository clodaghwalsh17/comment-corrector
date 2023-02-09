from comment_corrector.status import Status
from comment_corrector.category import Category

class Comment():

    def __init__(self, text, line_number, is_multiline, real_length=None, category=None):
        self.__text = text.strip() 
        self.__line_number = line_number
        self.__is_multiline = is_multiline        
        self.__category = category
        self.__status = Status.UNCHECKED

        if real_length:
            self.__real_length = real_length
        else:
            self.__real_length = len(text) + 1

    @classmethod
    # Construct an object using the Comment object of comment_parser as a base
    def from_comment_parser(cls, base_comment, category=None):
        return cls(base_comment.text(), base_comment.line_number(), base_comment.is_multiline(), category)

    def length(self):
        return len(self.__text)

    # Length of the comment including whitespace and the comment symbol
    def real_length(self):
        return self.__real_length
    
    def categorise_comment(self, category):
        self.__category = category
    
    def category(self):
        if self.__category is not None:
            return self.__category.name
        else:
            return ""
    
    def update_status(self, status):
        self.__status = status

    def comment_status(self):
        return self.__status.name

    def text(self):
        return self.__text
    
    def line_number(self):
        return self.__line_number
    
    def is_multiline(self):
        return self.__is_multiline
    
    def __str__(self):
        return self.__text

    def __repr__(self):
        return 'Comment(%s, %s, %s, %s, %s)' % (self.__text, self.__line_number, self.__is_multiline, self.__category.name, self.__status.name)  