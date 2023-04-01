class EditScriptAction:

    def __init__(self, type, src_start, src_end, dst_start=-1, dst_end=-1, affects_return=False):
        self.__type = type
        self.__src_start = src_start
        self.__src_end = src_end
        self.__dst_start = dst_start
        self.__dst_end = dst_end
        self.__affects_return = affects_return
    
    def type(self):
        return self.__type

    def src_start(self):
        return self.__src_start

    def src_end(self):
        return self.__src_end
    
    def dst_start(self):
        return self.__dst_start

    def dst_end(self):
        return self.__dst_end

    def affects_return(self):
        return self.__affects_return
    
    def __repr__(self):
        return 'EditScriptAction(%s, %d, %d, %d, %d, %r)' % (self.__type, self.__src_start, self.__src_end, self.__dst_start, self.__dst_end, self.__affects_return)  
