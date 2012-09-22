'''
Represents an ambiguous surface form detected by wikiminer in a short text on the site
'''
class Ambiguous_Entity:
    
    def __init__(self, entity_id, entity_text, 
                 tweet_id, tweet_text, 
                 username, candidates, site):
        self.entity_id = entity_id
        self.entity_text = entity_text
        self.tweet_id = tweet_id
        self.tweet_text = tweet_text
        self.username = username
        self.candidates = candidates
        self.site = site
        
        

        


