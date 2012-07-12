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
        
    def get_categories_to_num_edits_OLD(self):
        ''' Returns a mapping from category -> n, where each category is 
        a wikipedia category the user edited at least one article from and 
        where n is the total number of edits the user made to article(s) 
        within that category. '''
        category_to_num_edits = {}
        for hierarchy in self.__hierarchy_edits__:
            edits_on_hierarchy = self.__hierarchy_edits__[hierarchy]
            categories = hierarchy.get_category_to_distance().keys()
            for category in categories:
                if category in category_to_num_edits:
                    num_edits = category_to_num_edits[category]
                else:
                    num_edits = 0
                num_edits = num_edits + edits_on_hierarchy
                category_to_num_edits[category] = num_edits
        return category_to_num_edits
    
    def get_shortest_path(self, category):
        ''' Returns the lowest number of edges that must be traversed to reach 
        the given category in any of the user's category hierarchy graphs. '''
        min_distance = -1
        for category_hierarchy in self.__hierarchy_edits__:
            category_to_distance = category_hierarchy.get_category_to_distance()
            try:
                dist = category_to_distance[category]
                if dist < min_distance:
                    min_distance = dist
            except:
                continue
        return min_distance
            