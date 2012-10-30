"""
Finds named entities (Wikipedia resources) in a given full text string.

Uses DBPedia Spotlight's (http://dbpedia.org/spotlight) candidates
interface as well as Wikipedia Miner's (http://wikipedia-miner.cms.waikato.ac.nz)
services to identify possible DBPedia (named) entities for a given input string.
"""

from Ambiguous_Entity import CandidateResource
from CONSTANT_VARIABLES import BASELINE_WikipediaMiner, \
    BASELINE_DbpediaSpotlight
from urllib2 import Request, urlopen, URLError, HTTPError
import json
import pprint
import urllib

WIKIPEDIA_MINER_SEARCH_SERVICE_URI = \
    "http://wikipedia-miner.cms.waikato.ac.nz/services/search?"
    #"http://samos.mminf.univie.ac.at:8080/wikipediaminer/services/search?"

DBPEDIA_SPOTLIGHT_URI = "http://spotlight.dbpedia.org/rest/candidates?text="
# DBPEDIA_SPOTLIGHT_URI = "http://samos.mminf.univie.ac.at:2222/rest/candidates?text="

WIKIPEDIA_MINER_WIKIFY_SERVICE_URI = \
    "http://samos.mminf.univie.ac.at:8080/wikipediaminer/services/wikify?"
    
def find_named_entities_wikipedia_miner(text):
    """Finds named entities in a given text using Wikipedia Miner"""
    
    request_uri = WIKIPEDIA_MINER_WIKIFY_SERVICE_URI + "source=" + urllib.quote(text)
    request_uri += "&sourceMode=auto"
    request_uri += "&responseFormat=json"
    request_uri += "&disambiguationPolicy=loose"
    request_uri += "&minProbability=0"
    
    request = Request(request_uri)
    
    try:
        response = urlopen(request)
    except HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        
    result = json.loads(response.read())
    
    named_entities = []
    for topic in result['detectedTopics']:
        article_id = topic['id']
        title = topic['title']
        weight = topic['weight']
        dbpedia_uri = "http://dbpedia.org/resource/" + title.replace(" ", "_")
        entity = {'article_id': article_id, 'title': title, 'weight': weight,
                        'dbpedia_uri': dbpedia_uri}
        named_entities.append(entity)
    return named_entities

def find_candidates_wikipedia_miner(text):
    """ Finds all named entities in the given text and returns a mapping 
    of each named entity's surface form -> candidate resources
    
    An empty dict is returned if no entities were found. Entities for 
    which no candidate resources were found are not included in the map. """
    
    surface_form_to_candidates = {}
    result = query_wikipedia_miner_for_candidates(text)
    for entity_result in result['labels']:
        surface_form = entity_result['text'].lower()
        
        # handle multiple mentions of the same entity
        try:
            candidates = surface_form_to_candidates[surface_form]
        except:
            candidates = {} # candidate title -> candidate data
            
        for sense in entity_result['senses']:
            sense_title = sense['title'].replace(" ", "_")
            
            if sense_title in candidates:
                # already mapped entity to this candidate (must be the second 
                # mention of the same entity, and both mentions share this candidate)
                continue
            
            sense_dbpedia_uri = "http://dbpedia.org/resource/"+sense_title
            sense_score = sense['weight']
            
            cand_obj = CandidateResource(sense_title, sense_dbpedia_uri, (BASELINE_WikipediaMiner, sense_score))
            candidates[sense_title] = cand_obj
            
        if len(candidates)>0: # ignore entities that have no candidates
            surface_form_to_candidates[surface_form] = candidates 
    return surface_form_to_candidates
    
def find_candidates_dbpedia(text):
    """ Finds all named entities in the given text and returns a mapping 
    of each named entity's surface form -> candidate resources
    
    An empty dict is returned if no entities were found. Entities for 
    which no candidate resources were found are not included in the map. """
    
    surface_form_to_candidates = {}
    result = query_dbpedia_spotlight_for_candidates(text)
    surface_form_list = result['annotation']['surfaceForm']
    if isinstance(surface_form_list, dict):
        # for short text with a single detected entity, dbpedia just returns that one entity's
        # dict rather than a list containing it, so we need to put it in a list ourselves
        surface_form_list = [surface_form_list]
    for entity_result in surface_form_list:    
        surface_form = entity_result['@name'].lower()
        
        # handle multiple mentions of the same entity
        try:
            candidates = surface_form_to_candidates[surface_form]
        except:
            candidates = {} # candidate title -> candidate data
            
        # skip entities with no candidates, which will not have the 'resource' key
        if not 'resource' in entity_result:
            continue
        
        result_res_list = entity_result['resource']
        if isinstance(result_res_list, dict):
            # for NE with a single candidate, dbpedia just returns that one candidate's
            # dict rather than a list containing it, so we need to put it in a list ourselves
            result_res_list = [result_res_list]
        for res in result_res_list:
            res_title = res['@label'].replace(" ", "_")
            
            if res_title in candidates:
                # already mapped entity to this candidate (must be the second 
                # mention of the same entity, and both mentions share this candidate)
                continue
            
            res_dbpedia_uri = "http://dbpedia.org/resource/"+res_title
            res_score = res['@finalScore']

            cand_obj = CandidateResource(res_title, res_dbpedia_uri, (BASELINE_DbpediaSpotlight, res_score))
            candidates[res_title] = cand_obj
        
        if len(candidates)>0: # ignore entities that have no candidates
            surface_form_to_candidates[surface_form] = candidates
    return surface_form_to_candidates

def query_wikipedia_miner_for_candidates(text):   
    ''' Queries Wikipedia Miner's Search service 
    service and returns the server's JSON response '''

    request_uri = WIKIPEDIA_MINER_SEARCH_SERVICE_URI + "query=" + urllib.quote(text)
    request_uri += "&complex=true"
    request_uri += "&minPriorProbability=0"
    request_uri += "&responseFormat=json"
    
    request = Request(request_uri)
    try:
        print "Querying Wikipedia Miner for named entities and candidate resources..."
        response = urlopen(request)
    except HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        return
    except URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
        return
    result = json.loads(response.read())
    return result

def query_dbpedia_spotlight_for_candidates(text):
    ''' Queries DBPedia Spotlight's candidates service 
    service and returns the server's JSON response '''
    
    request_uri = DBPEDIA_SPOTLIGHT_URI + urllib.quote(text)
    request_uri += "&confidence=0"
    request_uri += "&support=0"
    
    request = Request(request_uri)
    request.add_header("Accept", "application/json")
    try:
        print "Querying DBPedia Spotlight for named entities and candidate resources..."
        response = urlopen(request)
    except HTTPError, e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    except URLError, e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    result = response.read()
    result = json.loads(result)
    return result

if __name__ == '__main__':
    #ne = find_named_entities("President Obama is the president of the USA")
    ne = find_named_entities_wikipedia_miner("Barack Obama is the president of the United States")
    pprint.pprint(ne)
    ne = find_named_entities_wikipedia_miner("Cornell is a university in Ithaca")
    pprint.pprint(ne)