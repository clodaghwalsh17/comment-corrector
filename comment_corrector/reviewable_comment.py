class ReviewableComment():

    def __init__(self, comment, errors, description=""):
        self.__text = comment.text()
        self.__line_number = comment.line_number()
        self.__errors = []
        self.__errors.extend(errors)
        self.__description = description

    def text(self):
        return self.__text

    def line_number(self):
        return self.__line_number
    
    def update_line_number(self, line_number):
        self.__line_number = line_number

    def description(self):
        return self.__description
    
    def add_description(self, description):
        self.__description = description
    
    def add_error(self, error):
        self.__errors.append(error)

    def get_errors(self):
        return self.__errors
    
    def __hash__(self):
        return hash((self.__text, self.__line_number))
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): 
            return NotImplemented
        return self.__text == other.text() and self.__line_number == other.line_number()
    
    def __str__(self):
        return self.__text

    def __repr__(self):
        return 'ReviewableComment(%s, %s, %s, %s)' % (self.__text, self.__line_number, self.__errors, self.__description)  