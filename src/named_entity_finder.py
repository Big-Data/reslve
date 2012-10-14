#!/usr/bin/env python
# encoding: utf-8
"""
Finds named enities (Wikipedia resources) in a given full text string.

Uses DBPedia Spotlight's (http://dbpedia.org/spotlight) candidates
interface as well as Wikipedia Miner's (http://wikipedia-miner.cms.waikato.ac.nz)
services to identify possible DBPedia (named) entities for a given input string.
"""

from urllib2 import Request, urlopen, URLError, HTTPError
from wikipedia import wikipedia_api_util
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
    
    if not 'labels' in result:
        return {}  # problem with this short text so just ignore it..
    
    surface_forms_to_candidates = __get_ne_candidate_map__(result, 'labels', 'text',
                                                           'senses', 'id', 'title', 'weight')
    return surface_forms_to_candidates 

def find_candidates_dbpedia(text, ambiguous_only=True):
    """ Finds all named entities in the given text and returns a mapping 
    of each named entity's surface form -> candidate resources
    
    An empty dict is returned if no entities were found. Entities for 
    which no candidate resources were found are not included in the map. """
    
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
    
    result_map = result['annotation']
    surface_forms_to_candidates = __get_ne_candidate_map__(result_map, 'surfaceForm', '@name', 
                                                           'resource', None, '@label', '@finalScore')
    return surface_forms_to_candidates 

def __get_ne_candidate_map__(result_map, ne_key, ne_text_key, 
                             candidate_key, cand_id_key, cand_title_key, cand_score_key):
    ''' returns a mapping of named entity text (ie surface
    form) to the candidate resources it may refer to '''
    surface_forms_to_candidates = {}
    for topic in result_map[ne_key]: # for each named entity..
        try:
            # the surface form of the named entity
            orig_text = topic[ne_text_key]
            
            # its candidate resources
            if not candidate_key in topic:
                continue # no candidates
            candidates = []
            result_cand_list = topic[candidate_key]
            if isinstance(result_cand_list, dict):
                # want the result_cand_list to be a list, but for NE with a single 
                # candidate, dbpedia just returns that one candidate's mapping rather
                # than a list containing it, so we need to put it in a list ourselves
                result_cand_list = [result_cand_list]
            for cand_res in result_cand_list:
                try:
                    # candidate resource's title
                    title = cand_res[cand_title_key]
                    
                    # candidate resource's URL on DBPedia
                    dbpedia_uri = "http://dbpedia.org/resource/" + title.replace(" ", "_")
                    
                    # candidate resource's wikipedia page ID
                    if cand_id_key != None:
                        article_id = cand_res[cand_id_key]
                    else:
                        article_id = wikipedia_api_util.query_page_id(title)
                    
                    # candidate's score (ie weight, probability) 
                    score = cand_res[cand_score_key]
                    
                    candidate = {'article_id': article_id, 'title': title, 
                                 'weight': score, 'dbpedia_uri': dbpedia_uri}
                    candidates.append(candidate)
                except:
                    # just ignore problematic candidate...
                    continue
                
            # might only care about ambiguous entities (those with more than a single candidate)
            if len(candidates)==0:
                continue
            surface_forms_to_candidates[orig_text] = candidates
        except: 
            # ignore problematic entities..
            continue
    return surface_forms_to_candidates

if __name__ == '__main__':
    #ne = find_named_entities("President Obama is the president of the USA")
    ne = find_named_entities_wikipedia_miner("Barack Obama is the president of the United States")
    pprint.pprint(ne)
    ne = find_named_entities_wikipedia_miner("Cornell is a university in Ithaca")
    pprint.pprint(ne)