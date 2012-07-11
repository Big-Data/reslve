'''
Represents a user in terms of the number of edits she has made on 
Wikipedia articles and their associated category hierarchy graphs. 
'''
class User:
    
    def __init__(self, username, hierarchy_edits):
        '''
        @param username: the username that this user utilizes 
            on both wikipedia and twitter
        @param hierarchy_edits: a mapping of Category_Hierarchy -> number of times
            this user has edited the article on which that hierarchy is built.
            For each article the user has edited on wikipedia, this hierarchy_edits 
            mapping should contain a key for that article's resulting hierarchy.
        '''
        self.__username__ = username
        self.__hierarchy_edits__ = hierarchy_edits
