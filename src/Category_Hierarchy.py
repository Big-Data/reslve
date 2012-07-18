'''
Represents the hierarchy graph of categories originating from a source article.
'''
class Category_Hierarchy:
    
    def __init__(self, source_article_id, category_to_distance):
        '''
        @param source_article_id: The id of the article from which 
            this category hierarchy originates
        @param category_to_distance: A mapping from category id -> number of 
            steps away from the source article that category is positioned 
            in this category hierarchy graph
        '''
        self.__source_article_id__ = source_article_id
        self.__category_to_distance__ = category_to_distance
        
    def get_source_article_id(self):
        return self.__source_article_id__
    
    def get_category_distance(self, category):
        ''' For a given category, returns the number of steps away from the 
        source article that category is positioned in this hierarchy '''
        if not category in self.__category_to_distance__:
            return 0
        return self.__category_to_distance__[category]
        
    def get_category_to_distance(self):
        ''' Returns a mapping from category id to the number of steps 
        away from the source article that the category is positioned 
        in this category hierarchy graph '''
        return self.__category_to_distance__

    def is_category_in_hierarchy(self, category):
        return category in self.__category_to_distance__
    
    def get_category_list(self):
        ''' Returns a list of all categories in this hierarchy '''
        return self.__category_to_distance__.keys()
