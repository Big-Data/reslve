"""
Finds named entities (Wikipedia resources) in a given full text string.

Uses DBPedia Spotlight's (http://dbpedia.org/spotlight) candidates
interface as well as Wikipedia Miner's (http://wikipedia-miner.cms.waikato.ac.nz)
services to identify possible DBPedia (named) entities for a given input string.
"""

from Ambiguous_Entity import CandidateResource
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
    
def find_ne_to_candidates(text):
    ''' Returns the union of named entities detected in a 
    given text by both Wikipedia Miner and DBPedia Spotlight '''
    
    # find the named entities and candidates detected by each toolkit
    sf_to_candidates_wikiminer = find_candidates_wikipedia_miner(text)
    sf_to_candidates_dbpedia = find_candidates_dbpedia(text)
    
    # merge the candidates of the surface forms detected by both services
    sf_to_candidates_union = __merge_sf_maps__(sf_to_candidates_wikiminer, sf_to_candidates_dbpedia)
    return sf_to_candidates_union

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
    
    result = query_wikipedia_miner_for_candidates(text)
    surface_form_to_candidates = {}
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
            
            cand_obj = CandidateResource(sense_title, sense_dbpedia_uri, sense_score, CandidateResource.SCORE_NOT_AVAILBLE)
            candidates[sense_title] = cand_obj
            
        if len(candidates)>0: # ignore entities that have no candidates
            surface_form_to_candidates[surface_form] = candidates 
    return surface_form_to_candidates
    
def find_candidates_dbpedia(text):
    """ Finds all named entities in the given text and returns a mapping 
    of each named entity's surface form -> candidate resources
    
    An empty dict is returned if no entities were found. Entities for 
    which no candidate resources were found are not included in the map. """
    
    result = query_dbpedia_spotlight_for_candidates(text)
    surface_form_to_candidates = {}
    
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

            cand_obj = CandidateResource(res_title, res_dbpedia_uri, CandidateResource.SCORE_NOT_AVAILBLE, res_score)
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

def __merge_sf_maps__(sf_to_candidates_wikiminer, sf_to_candidates_dbpedia):

    # start with the entities detected by wikiminer
    sf_to_candidates_union = sf_to_candidates_wikiminer 
    
    # then add all the entities detected by dbpedia, 
    # merging candidates for ones also detected by wikiminer
    for surface_form in sf_to_candidates_dbpedia:
        if not surface_form in sf_to_candidates_union:
            # entity not detected by wikiminer, so can just add it to union map
            sf_to_candidates_union[surface_form] = sf_to_candidates_dbpedia[surface_form]
            continue
        
        # otherwise, need to merge the candidate objects...
        
        # start with candidates detected by wikiminer
        union_candidates = sf_to_candidates_union[surface_form]
        
        # then add in missing dbpedia candidates or scores
        dbpedia_candidates = sf_to_candidates_dbpedia[surface_form]
        for cand_title in dbpedia_candidates:
            if not cand_title in union_candidates:
                # candidate not detected by wikiminer, so can just add it
                union_candidates[cand_title] = dbpedia_candidates[cand_title]
                continue
            
            # otherwise, candidate detected by both
            # services so will have a score from each
            cand_obj = union_candidates[cand_title]
            
            # set its dbpedia score
            cand_obj.dbpedia_score = dbpedia_candidates[cand_title].dbpedia_score
            union_candidates[cand_title] = cand_obj
            
        # update the sf -> candidates
        sf_to_candidates_union[surface_form] = union_candidates  
    return sf_to_candidates_union

if __name__ == '__main__':
    #ne = find_named_entities("President Obama is the president of the USA")
    ne = find_named_entities_wikipedia_miner("Barack Obama is the president of the United States")
    pprint.pprint(ne)
    ne = find_named_entities_wikipedia_miner("Cornell is a university in Ithaca")
    pprint.pprint(ne)