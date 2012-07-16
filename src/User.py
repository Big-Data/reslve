'''
Represents a user in terms of the number of edits she has made on 
Wikipedia articles and their associated category hierarchy graphs. 
'''
class User:
    
    def __init__(self, username, hierarchy_edits, category_edits):
        '''
        @param username: the username that this user utilizes 
            on both wikipedia and twitter
        @param hierarchy_edits: a mapping of Category_Hierarchy -> number of times
            this user has edited the article on which that hierarchy is built.
            For each article the user has edited on wikipedia, this hierarchy_edits 
            mapping should contain a key for that article's resulting hierarchy.
        @param category_edits: a mapping of category ID -> number of edits that the 
        user made on article(s) belonging to that category
        '''
        self.__username__ = username
        self.__hierarchy_edits__ = hierarchy_edits
        self.__category_edits__ = category_edits
        
    def get_username(self):
        return self.__username__
        
    def get_categories_to_num_edits(self):
        return self.__category_edits__
    
    def get_category_hierarchies(self):
        return self.__hierarchy_edits__
        
    def get_shortest_path(self, category):
        ''' Returns the lowest number of edges that must be traversed to reach 
        the given category in any of the user's category hierarchy graphs. '''
        min_distance = -1
        for category_hierarchy in self.__hierarchy_edits__:
            category_to_distance = category_hierarchy.get_category_to_distance()
            try:
                dist = category_to_distance[category]
                if min_distance==-1 or dist < min_distance:
                    min_distance = dist
            except:
                continue
        return min_distance
    
    def get_category_list(self):
        ''' Returns a list category IDs of all the categories in this query's hierarchies ''' 
        return self.__category_edits__.keys()
            