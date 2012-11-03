#!/usr/bin/env python
# encoding: utf-8
"""
knowledge_graph.py: Provides access to concepts in knowledge
graphs and computes various metrics.

"""

import pprint

class DBPediaCategories(object):
    """An in-memory representation of the DBPedia/Wikipedia category
    network, based on the SKOS DBPedia Category system, which an be downloaded
    at: http://wiki.dbpedia.org/Downloads38
    
    The API assumes that all category URIs are normalized to their category
    identifier:
    
    http://en.wikipedia.org/wiki/Category:Houses -> Category:Houses
    http://dbpedia.org/resource/Category:Houses -> Category:Houses
    
    """
    
    DBPEDIA_PREFIX = "http://dbpedia.org/resource/"

    # SKOS Resource URIs
    SKOS_CONCEPT = "http://www.w3.org/2004/02/skos/core#Concept"
    SKOS_BROADER = "http://www.w3.org/2004/02/skos/core#broader"
    SKOS_NARROWER = "http://www.w3.org/2004/02/skos/core#narrower"
    SKOS_RELATED = "http://www.w3.org/2004/02/skos/core#related"

    # Property URIs
    SKOS_PREFLABEL = "http://www.w3.org/2004/02/skos/core#prefLabel"
    RDF_TYPE_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    
    def __init__(self, category_file):
        print "*** Initializing DBPedia categories ***"
        self.categories = {}
        self.load_from_file(category_file)
        
    def load_from_file(self, nt_file):
        print "Loading DBPedia category file %s ..." % nt_file
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
                self.add_relation(category, 'broader', broader_category)
            elif predicate == DBPediaCategories.SKOS_NARROWER:
                category = subject_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                narrower_category = object_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                self.add_relation(category, 'narrower', narrower_category)
            elif predicate == DBPediaCategories.SKOS_RELATED:
                category = subject_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                related_category = object_node[len(
                                        DBPediaCategories.DBPEDIA_PREFIX):]
                self.add_relation(category, 'related', related_category)
            elif predicate == DBPediaCategories.SKOS_PREFLABEL:
                # Ignore for the moment
                pass
            else:
                print "Skipping line: %s" % line
        
    def get_neighbors(self, category, relation='broader', distance=1):
        """Returns a list of neighbors for a given category"""
        if distance == 0:
            return None
        else:
            neighbors = []
            for neighbor in self.categories[category][relation]:
                neighbors.append(neighbor)
                next_neighbors = self.get_neighbors(neighbor, relation,
                                                    distance=distance-1)
                if next_neighbors is not None:
                    neighbors = neighbors + next_neighbors
        return neighbors
        
    def compute_distance(self, uri, other_uri):
        """Computes the shortest path between two category nodes"""
        pass # TBD (implement via iGraph or NetworkX)
        
    # private stuff
    def add_category(self, category):
        """Add a DBpedia category (= network node)"""
        if category not in self.categories:
            self.categories.setdefault(category, {})
            self.categories[category].setdefault('broader', [])
            self.categories[category].setdefault('narrower', [])
            self.categories[category].setdefault('related', [])

    def add_relation(self, src_category, relation, tgt_category):
        """Add a relationship between DBPedia categories ( = network edges)"""
        if tgt_category not in self.categories:
            self.add_category(tgt_category)
        self.categories[src_category][relation].append(tgt_category)

def usage_example():
    # Running the script
    
    dbpedia_categories_file = "/Users/elizabethmurnane/git/reslve/data/skos_categories_en_10000.nt"
    # dbpedia_categories_file = "skos_categories_en.nt"
    
    dbpedia_categories = DBPediaCategories(dbpedia_categories_file)
    
    print "Parsed %d categories" % len(dbpedia_categories.categories)
    
    #pprint.pprint(dbpedia_categories.categories['Category:Swedish_monarchs'])
    
    pprint.pprint(dbpedia_categories.get_neighbors('Category:Swedish_monarchs', 
                                distance=1))
    pprint.pprint(dbpedia_categories.get_neighbors('Category:Swedish_monarchs', 
                                distance=2))
    pprint.pprint(dbpedia_categories.get_neighbors('Category:Swedish_monarchs', 
                                distance=3))
    pprint.pprint(dbpedia_categories.get_neighbors('Category:Swedish_monarchs', 
                                distance=4))                            