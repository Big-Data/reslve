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

def find_named_entities(text):
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
    

if __name__ == '__main__':
    ne = find_named_entities("President Obama is the president of the USA")
    pprint.pprint(ne)