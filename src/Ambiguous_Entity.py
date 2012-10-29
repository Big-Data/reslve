'''
Represents an ambiguous surface form detected by wikiminer in a short text on the site
'''
from wikipedia import wikipedia_api_util
import text_util

class NamedEntity:
    ''' Represents a named entity detected in a short text.
    We use the entity's surface form as its unique identifier. That means that
    for short texts containing multiple entities with the same surface form, 
    we'll treat all occurrences as a single entity. '''
    
    def __init__(self, surface_form,
                 shorttext_id, shorttext_str,
                 username, site):
        '''
        @param surface_form: the surface form of the named entity this object represents
        @param shorttext_id: the ID of the short text that contains this entity
        @param shorttext_str: the string of the short text that contains this entity
        @param username: the username who authored the short text containing this entity
        @param site: the site on which the short text containing this entity was posted
        '''
        self.surface_form = surface_form
        self.shorttext_id = shorttext_id
        self.shorttext_str = shorttext_str
        self.username = username
        self.site = site
        
        # initialize the baseline candidate rankings, which each be a mapping 
        # from a candidate resource's title to its CandidateResource object
        self.wikipedia_miner_ranking = {}
        self.dbpedia_spotlight_ranking = {}
    
    def set_wikipedia_miner_ranking(self, wikipedia_miner_ranking):
        ''' @param wikipedia_miner_ranking: a ranking of CandidateResources according to Wikipedia Miner, 
        which should be a dict of candidate resource title to CandidateResource object ''' 
        self.wikipedia_miner_ranking = wikipedia_miner_ranking
        
    def set_dbpedia_spotlight_ranking(self, dbpedia_spotlight_ranking):
        ''' @param dbpedia_spotlight_ranking: a ranking of CandidateResources according to DBPedia Spotlight,
        which should be a dict of candidate resource title to CandidateResource object  '''  
        self.dbpedia_spotlight_ranking = dbpedia_spotlight_ranking
        
    def get_entity_id(self):
        ''' Using the containing short text's ID concatenated 
        with this entity's surface form as the entity's ID '''
        return str(self.shorttext_id)+"_"+str(self.surface_form)
        
    def is_valid_entity(self):
        ''' @return: True if this is a valid named entity, otherwise returns False. 
        Currently the requirements are that this entity is at least two characters and is a noun.'''
        if len(self.surface_form)<=1:
            return False # ignore single characters, which are probably resulting from buggy apostrophe stuff..
        
        nouns = text_util.get_nouns(self.shorttext_str, self.site)
        surface_form_tokens = self.surface_form.split()
        for sft in surface_form_tokens:
            if not sft in nouns:
                return False
        return True
    
    def get_candidate_URIs(self):
        ''' Returns the URIs of all the candidate resources 
        detected by wikipedia miner and/or dbpedia spotlight '''
        wikiminer_cand_objs = self.wikipedia_miner_ranking
        dbpedia_cand_objs = self.dbpedia_spotlight_ranking
        
        wikiminer_cand_uris = set([candidate_obj.get_wikipedia_page() for candidate_obj in wikiminer_cand_objs.values()])
        dbpedia_cand_uris = set([candidate_obj.get_wikipedia_page() for candidate_obj in dbpedia_cand_objs.values()])
        candidate_URIs = list(wikiminer_cand_uris.union(dbpedia_cand_uris))
        return candidate_URIs   
    
#    def get_valid_candidate_URIs(self):
#        ''' Returns the URIs of the candidate resources for this entity
#        that are "valid", ie currently we only consider entities that are 
#        a Person, Place, Organization, etc (see VALID_RDF_TYPES) '''
#        wikiminer_cand_objs = self.wikipedia_miner_ranking
#        dbpedia_cand_objs = self.dbpedia_spotlight_ranking
#        valid_candidate_resources = self.__validate_candidates__(wikiminer_cand_objs, [])
#        valid_candidate_resources = self.__validate_candidates__(dbpedia_cand_objs, valid_candidate_resources)
#        return valid_candidate_resources
#    def __validate_candidates__(self, candidate_objs, already_validated):
#        valid_candidate_resources = []
#        for candidate_title in candidate_objs:
#            try:
#                candidate_obj = candidate_objs[candidate_title]
#                candidate_wikipage = candidate_obj.get_wikipedia_page()
#                if candidate_wikipage in already_validated:
#                    continue # already validated this candidate
#            
#                response = urllib2.urlopen("http://dbpedia.org/data/"+candidate_title+".json").read()
#                response = simplejson.loads(response.decode('utf-8'))
#                resource_data = response[candidate_obj.dbpedia_uri]
#                
#                if self.__is_candidate_valid_type__(resource_data):
#                    valid_candidate_resources.append(candidate_wikipage)
#            except:
#                continue # ignore problematic candidates       
#        return valid_candidate_resources 
#    def __is_candidate_valid_type__(self, candidate_data):
#        rdftype_key = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
#        if not rdftype_key in candidate_data: # has no type
#            return False
#
#        rdf_types = candidate_data[rdftype_key]
#        for type_tuple in rdf_types:
#            if type_tuple['value'] in VALID_RDF_TYPES:
#                return True
#        
#        # none of its associated types are what we consider valid
#        return False
    
class CandidateResource:
    ''' Represents a candidate resource that an ambiguous named entity may refer to. ''' 
        
    def __init__(self, title, dbpedia_URI, score):
        '''
        @param title: The title of this candidate's wikipedia/dbpedia page (same thing) 
        @param dbpedia_URI: The URI of this candidate's dbpedia resource page
        @param score: A tuple of (algorithm_id, float_score) where algorithm is the id of
        the service or RESLVE ranking function that calculated and returned the float score.
        Note that float score is the score output by the service or algorithm ie it doesn't 
        have to be normalized to be between 0-1 because that will be done elsewhere
        '''
        self.title = title
        self.dbpedia_URI = dbpedia_URI
        self.score = score
        
    def get_wikipedia_page(self):
        return wikipedia_api_util.get_wikipedia_page_url(self.title.replace(' ', '_'))        