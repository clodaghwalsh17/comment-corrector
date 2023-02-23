class Comment():

    def __init__(self, text, line_number, is_multiline, real_length=None, category=None):
        self.__text = text.strip() 
        self.__line_number = line_number
        self.__is_multiline = is_multiline        
        self.__category = category

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
    
    # Comments are categorised using the enum Category
    def categorise_comment(self, category):
        self.__category = category
    
    def category(self):
        return self.__category

    def text(self):
        return self.__text

    def update_text(self, text):
        self.__text = text
    
    def line_number(self):
        return self.__line_number
    
    def is_multiline(self):
        return self.__is_multiline

    def __hash__(self):
        return hash((self.__text, self.__line_number, self.__is_multiline, self.__category))
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): 
            return NotImplemented
        return self.__text == other.text() and self.__line_number == other.line_number() and self.__is_multiline == other.is_multiline() and self.__category == other.category()    

    def __str__(self):
        return self.__text

    def __repr__(self):
        return 'Comment(%s, %s, %s, %s)' % (self.__text, self.__line_number, self.__is_multiline, self.category())  