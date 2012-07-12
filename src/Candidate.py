'''
Represents a candidate named entity.
'''
class Candidate:
    
    def __init__(self, candidate_ID, dbpedia_URI, title, wikiminer_weight, category_hierarchy):
        '''
        @param candidate_ID: the ID of the article resource that corresponds to this candidate
        @param dbpedia_URI: the dbpedia URL of the article that corresponds to this candidate
        @param title: the title of the article that corresponds to this candidate
        @param wikiminer_weight: the weight wikiminer computes for this candidate, which "is 
        larger for senses that are likely to be the correct interpretation of the query"
        @param category_hierarchy: a Category_Hierarchy that originates from
        the candidate's associated article
        '''
        self.__candidate_ID__ = candidate_ID
        self.__dbpedia_URI__ = dbpedia_URI
        self.__title__ = title
        self.__wikiminer_weight__ = wikiminer_weight
        self.__category_hierarchy__ = category_hierarchy
        
    def get_candidateID(self):
        return self.__candidate_ID__

    def get_category_hierarchy(self):
        return self.__category_hierarchy__
    