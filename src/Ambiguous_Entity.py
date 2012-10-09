'''
Represents an ambiguous surface form detected by wikiminer in a short text on the site
'''
from CONSTANT_VARIABLES import VALID_RDF_TYPES
from wikipedia import wikipedia_api_util
import simplejson
import text_util
import urllib2
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
        
    def is_valid_entity(self):
        ''' If is a valid Named Entity with more than one valid candidates, 
        returns a list of those valid candidates. Otherwise, returns an empty list '''
        nouns = text_util.get_nouns(self.shorttext_str, self.site)
        if not self.entity_str in nouns:
            # named entity must be a noun
            return []
        valid_candidates = self.__get_valid_candidates__()
        return valid_candidates
    
    def __get_valid_candidates__(self):
        ''' Returns the URIs of the candidate resources for this entity
        that are "valid", ie currently we only consider entities that may 
        be a Person, Place, Organization, etc (see VALID_RDF_TYPES) '''
        #print "Candidates of "+str(self.entity_str)+" are: "+str([candidate['dbpedia_uri'] for candidate in self.candidates])
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