class EditScriptAction:

    def __init__(self, type, start_position, end_position, destination=-1):
        self.__type = type
        self.__start_position = start_position
        self.__end_position = end_position
        self.__destination = destination
    
    def type(self):
        return self.__type

    def start_position(self):
        return self.__start_position

    def end_position(self):
        return self.__end_position
    
    def destination(self):
        return self.__destination

    def __repr__(self):
        return 'EditScriptAction(%s, %s, %s, %s)' % (self.__type, self.__start_position, self.__end_position, self.__destination)  
