#!/usr/bin/env python
# encoding: utf-8
"""
knowledge_graph.py: Provides access to concepts in knowledge
graphs and computes various metrics.

"""

import pprint

class DBPediaCategories(object):

    DBPEDIA_PREFIX = "http://dbpedia.org/resource/"

    # SKOS URIs
    SKOS_CONCEPT = "http://www.w3.org/2004/02/skos/core#Concept"
    SKOS_BROADER = "http://www.w3.org/2004/02/skos/core#broader"
    SKOS_NARROWER = "http://www.w3.org/2004/02/skos/core#narrower"
    SKOS_RELATED = "http://www.w3.org/2004/02/skos/core#related"

    # Property URIs
    RDF_TYPE_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    
    def __init__(self):
        print "*** Initializing DBPedia categoris ***"
        self.categories = {}
        
    def load_from_file(self, nt_file):
        """Parses the DBpedia categories RDF file"""
        for line in open(nt_file, 'r'):
            spo = line.strip().split(" ", 4)[0:3] # Split into [S|P|O]
            subject_node = spo[0][1:-1] # strip < and >
            predicate = spo[1][1:-1] # strip < and >
            object_node = spo[2][1:-1]
            # parse rdf:type statements
            if predicate == DBPediaCategories.RDF_TYPE_URI:
                if object_node == DBPediaCategories.SKOS_CONCEPT:
                    category = subject_node[len(
                                            DBPediaCategories.DBPEDIA_PREFIX):]
                    self.add_category(category)
            elif predicate == DBPediaCategories.SKOS_BROADER:
                category = subject_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                broader_category = object_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                self.add_broader_category(category, broader_category)
            elif predicate == DBPediaCategories.SKOS_NARROWER:
                category = subject_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                broader_category = object_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                self.add_narrower_category(category, broader_category)
            # else:
            #     print "Unprocessed predicate: %s" % predicate
        
    def get_parent_categories(self, uri, distance=1):
        """Returns a list of parents for a given uri"""
        
    def compute_distance(self, uri, other_uri):
        """Computes the shortest path between two category nodes"""
        
    # private stuff
    def add_category(self, category):
        if category not in self.categories:
            self.categories.setdefault(category, {})
        
    def add_broader_category(self, category, broader_category):
        self.categories[category].setdefault('broader', [])
        if broader_category not in self.categories:
            self.categories.setdefault(broader_category, {})
        self.categories[category]['broader'].append(broader_category)

    def add_narrower_category(self, category, narrower_category):
        self.categories[category].setdefault('narrower', [])
        if narrower_category not in self.categories:
            self.categories.setdefault(narrower_category, {})
        self.categories[category]['narrower'].append(narrower_category)


# Running the script

dbpedia_categories_file = "data/skos_categories_en_1000.nt"

dbpedia_categories = DBPediaCategories()
dbpedia_categories.load_from_file(dbpedia_categories_file)

#pprint.pprint(dbpedia_categories.categories)

print "Parsed %d categories" % len(dbpedia_categories.categories)
