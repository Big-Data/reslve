'''
Represents an ambiguous surface form detected by wikiminer in a short text on the site
'''
class Ambiguous_Entity:
    
    def __init__(self, entity_id, entity_str, 
                 shorttext_id, shorttext_str, 
                 username, candidates, site):
        self.entity_id = entity_id
        self.entity_str = entity_str
        self.shorttext_id = shorttext_id
        self.shorttext_str = shorttext_str
        self.username = username
        self.candidates = candidates
        self.site = site
        
    def get_candidates(self):
        try:
            return [cand['title'] for cand in self.candidates]
        except:
            raise
            return []
