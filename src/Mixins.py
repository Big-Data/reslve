''' 
A module to store mixin classes, ie abstract base classes that just
provide common functionality and are not intended to be instantiated. 
'''

class EqualityMixin(object):
    
    def is_equal(self, other):
        ''' Should be implemented by subclasses '''
        raise Exception("is_equal not implemented "+str(self))

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.is_equal(other))
            #and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)
