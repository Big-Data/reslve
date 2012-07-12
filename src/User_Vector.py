class User_Vector:
    
    def __init__(self, username, weighted_category_vector):
        self.__username__ = username
        self.__weighted_category_vector__ = weighted_category_vector

    def get_weighted_vector(self):
        ''' Returns the weighted vector of category -> weight '''
        return self.__weighted_category_vector__