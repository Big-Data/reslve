''' 
Stores a user's username and a mapping from category -> n, where
each category is a wikipedia category the user edited at least 
one article from and where n is the actual number of edits the 
user made to articles with that category.
'''
import re
class User_Categories:
    
    def __init__(self, username):
        self.__username__ = username
        self.__category_map__ = {}
        
    def get_username(self):
        return self.__username__
    
    def get_categories(self):
        return self.__category_map__
    
    def add_categories(self, categories):
        for category in categories:
            self.add_category(category)
        
    def add_category(self, category):
        
        # format category name
        category = self.__format_category__(category)
        
        if ''==category:
            return
        
        if self.__category_map__.has_key(category):
            value = self.__category_map__[category]
        else:
            value = 0
        self.__category_map__[category] = value+1
        
    ''' Formats the category string:
    - a. remove "Category:" namespace
    - b. make lowercase
    - c. remove non-words like punctuation and numbers
    - d. remove leading and trailing white space
    '''
    def __format_category__(self, category):
        category = category.replace("Category:", "") #a
        category = category.lower() #b
        category = ''.join([c for c in category if re.match("[a-z\-\' \n\t]", c)]) #c
        category = category.strip() #d
        return category
        
        
