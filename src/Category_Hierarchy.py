'''
Represents the hierarchy graph of categories originating from a source article.
'''
class Category_Hierarchy:
    
    def __init__(self, source_article_id, category_to_distance):
        '''
        @param source_article_id: The id of the article from which 
            this category hierarchy originates
        @param category_to_distance: A mapping from category id -> number of 
            steps away  from the source article that category is positioned 
            in this category hierarchy graph
        '''
        self.__source_article_id__ = source_article_id
        self.__category_to_distance__ = category_to_distance
