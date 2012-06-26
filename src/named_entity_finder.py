#!/usr/bin/env python
# encoding: utf-8
"""
named_entity_finder.py: Find named enities (Wikipedia resources) in a given
full text string.

The NEntityFinder uses DBPedia Spotlight's (http://dbpedia.org/spotlight)
candidates interface to identify possible DBPedia (named) entities for a
given input string.

Example query: http://spotlight.dbpedia.org/rest/candidates?
                text=Barack%20Obama%20is%20the%20president%20of%20the%20USA

Created by Bernhard Haslhofer on 2012-05-01.
Copyright (c) Cornell University. All rights reserved.
"""

from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import json

import pprint

DBPEDIA_SPOTLIGHT_URI = "http://spotlight.dbpedia.org/rest/candidates?text="

# DBPEDIA_SPOTLIGHT_URI = "http://samos.mminf.univie.ac.at:2222/rest/candidates?text="

WIKIPEDIA_MINER_URI = \
    "http://samos.mminf.univie.ac.at:8080/wikipediaminer/services/search?"
    #"http://samos.mminf.univie.ac.at:8080/wikipediaminer/services/wikify?"


def find_named_entities_dbpedia(text):
    """Finds named entities in a given text and returns a dictionary of
    possible DBPedia entities for each possible match; an empty dict is
    returned if no entities were found.
    
    surfaceform: the matching tokens as they appear in the input string.
    
    """
    request = Request(DBPEDIA_SPOTLIGHT_URI + urllib.quote(text))
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
    
    named_entities = json.loads(result)
    
    return named_entities

def find_named_entities_wikipedia_miner(text):
    """Finds named entities in a given text using Wikipedia Miner"""
    
    request_uri = WIKIPEDIA_MINER_URI + "query=" + urllib.quote(text)
    request_uri += "&complex=true"
    request_uri += "&responseFormat=json"
    
    '''
    request_uri = WIKIPEDIA_MINER_URI + "source=" + urllib.quote(text)
    request_uri += "&sourceMode=auto"
    request_uri += "&responseFormat=json"
    request_uri += "&disambiguationPolicy=loose"
    '''
    
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
    
    named_entities = {}
    for topic in result['labels']:
        text = topic['text']
        candidates = []
        for sense in topic['senses']:
            article_id = sense['id']
            title = sense['title']
            weight = sense['weight']
            dbpedia_uri = "http://dbpedia.org/resource/" + title.replace(" ", "_")
            candidate = {'article_id': article_id, 'title': title, 'weight': weight,
                        'dbpedia_uri': dbpedia_uri}
            candidates.append(candidate)
        named_entities[text] = candidates    
    
    '''
    named_entities = []
    
    for topic in result['detectedTopics']:
        article_id = topic['id']
        title = topic['title']
        weight = topic['weight']
        dbpedia_uri = "http://dbpedia.org/resource/" + title.replace(" ", "_")
        entity = {'article_id': article_id, 'title': title, 'weight': weight,
                        'dbpedia_uri': dbpedia_uri}
        named_entities.append(entity)
    '''
    
    return named_entities
    

if __name__ == '__main__':
    #ne = find_named_entities("President Obama is the president of the USA")
    ne = find_named_entities_wikipedia_miner("Barack Obama is the president of the United States")
    pprint.pprint(ne)
    ne = find_named_entities_wikipedia_miner("Cornell is a university in Ithaca")
    pprint.pprint(ne)