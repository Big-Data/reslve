'''
Represents an ambiguous surface form detected by wikiminer in a short text on the site
'''
from CONSTANT_VARIABLES import VALID_RDF_TYPES
from Mixins import EqualityMixin
from wikipedia import wikipedia_api_util
import simplejson
import text_util
import urllib2

class NamedEntity:
    ''' Represents a named entity detected in a short text '''
    
    def __init__(self, entity_str, entity_offset,
                 shorttext_id, shorttext_str,
                 candidate_res_objs, 
                 username, site):
        '''
        @param entity_str: the surface form of the named entity this object represents
        @param entity_offset: the offset of this named entity within the containing short text
        @param shorttext_id: the ID of the short text that contains this entity
        @param shorttext_str: the string of the short text that contains this entity
        @param candidate_res_objs: a list of Candidate_Resource objects that this named entity could refer to
        @param username: the username who authored the short text containing this entity
        @param site: the site on which the short text containing this entity was posted
        '''
        self.entity_str = entity_str
        self.entity_offset = entity_offset
        self.shorttext_id = shorttext_id
        self.shorttext_str = shorttext_str
        self.candidate_res_objs = candidate_res_objs
        self.username = username
        self.site = site
        
    def is_valid_entity(self):
        ''' @return: True if this is a valid named entity, ie is a noun
        with at least one candidate of a valid type (Person, Place, Organization, 
        etc according to the candidate's rdftypes property). Otherwise, returns false. '''
        nouns = text_util.get_nouns(self.shorttext_str, self.site)
        if not self.entity_str in nouns:
            # named entity must be a noun
            return False
        valid_candidates = self.__get_valid_candidate_URIs__()
        return (len(valid_candidates)>0)
    
    def __get_valid_candidate_URIs__(self):
        ''' Returns the URIs of the candidate resources for this entity
        that are "valid", ie currently we only consider entities that are 
        a Person, Place, Organization, etc (see VALID_RDF_TYPES) '''
        #print "Candidates of "+str(self.entity_str)+" are: "+\
        #str([candidate['dbpedia_uri'] for candidate in self.candidates])
        valid_candidate_resources = []
        for candidate in self.candidates:
            try:
                candidate_title = candidate['title'].replace(' ', '_')
                dbpedia_uri = candidate['dbpedia_uri']
            
                response = urllib2.urlopen("http://dbpedia.org/data/"+candidate_title+".json").read()
                response = simplejson.loads(response.decode('utf-8'))
                resource_data = response[dbpedia_uri]
                
                if self.__is_candidate_valid_type__(resource_data):
                    candidate_wikipage = wikipedia_api_util.get_wikipedia_page_url(candidate_title)
                    valid_candidate_resources.append(candidate_wikipage)
            except:
                continue # ignore problematic candidates
        return valid_candidate_resources

    def __is_candidate_valid_type__(self, candidate_data):
        rdftype_key = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if not rdftype_key in candidate_data: # has no type
            return False

        rdf_types = candidate_data[rdftype_key]
        for type_tuple in rdf_types:
            if type_tuple['value'] in VALID_RDF_TYPES:
                return True
        
        # none of its associated types are what we consider valid
        return False
    
class CandidateResource(EqualityMixin):
    ''' Represents a candidate resource that an ambiguous named entity may refer to.
    Depending on whether the entity was detected by DBPedia Spotlight, Wikipedia Miner, or
    both, this object stores those services' scores that this candidate is the correct one ''' 
    
    SCORE_NOT_AVAILBLE_VALUE = 'Score_Unavailable'
    
    def __init__(self, title, dbpedia_URI, scores={}, wikipedia_pageID=None):
        '''
        @param title: The title of this candidate's wikipedia/dbpedia page (same thing) 
        @param dbpedia_URI: The URI of this candidate's dbpedia resource page
        @param scores: The score(s) for this candidate from DBPedia Spotlight, 
                       Wikipedia Miner, or both. Will be a mapping from 
                       DBPEDIA_SPOTLIGHT_SCORE_KEY->int, WIKIPEDIA_MINER_SCORE_KEY->int
        @param wikipedia_pageID: The ID of this candidate's wikipedia article page
        '''
        self.title = title
        self.dbpedia_URI = dbpedia_URI
            
        # Make sure each type of service has a key for its score,
        # evven if that service did not detect this entity/candidate
        self.scores = scores
        if not self.DBPEDIA_SPOTLIGHT_SCORE_KEY in scores:
            scores[self.DBPEDIA_SPOTLIGHT_SCORE_KEY] = self.SCORE_NOT_AVAILBLE
        if not self.WIKIPEDIA_MINER_SCORE_KEY in scores:
            scores[self.WIKIPEDIA_MINER_SCORE_KEY] = self.NOT_AVAILBLE
            
        # If page ID not supplied, determine it from the page title
        self.wikipedia_pageID = wikipedia_pageID
        if self.wikipedia_pageID is None:
            self.wikipedia_pageID = wikipedia_api_util.query_page_id(title)
                
        def is_equal(self, other):
            print "self.dict??"
            print self.dict
            
