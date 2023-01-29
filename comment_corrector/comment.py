class Comment():

    def __init__(self, text, line_number, is_multiline, category=""):
        self.__text = text
        self.__line_number = line_number
        self.__is_multiline = is_multiline
        self.__category = category

    @classmethod
    # Construct an object using the Comment object of comment_parser as a base
    def from_comment_parser(cls, base_comment, category=""):
        return cls(base_comment.text(), base_comment.line_number(), base_comment.is_multiline(), category)

    def calc_comment_length(self):
        return len(self.__text())
    
    def categorise_comment(self, category):
        self.__category = category
    
    def category(self):
        return self.__category
    
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