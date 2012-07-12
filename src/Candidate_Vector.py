class Candidate_Vector:
    
    def __init__(self, candidate_URI, weighted_category_vector):
        self.__candidate_URI__ = candidate_URI
        self.__weighted_category_vector__ = weighted_category_vector

    # Returns the wikipedia page URI of this candidate
    def get_candidate_URI(self):
        return self.__candidate_URI__
    
    def get_weighted_vector(self):
        ''' Returns the weighted vector of category -> weight '''
        return self.__weighted_category_vector__
