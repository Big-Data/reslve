'''
Constructs the category hierarchy graph originating from a particular Wikipedia article. This
hierarchy is represented using a Category_Hierarchy object, which stores the source article's
ID as well as a mapping from the ID of each category node in the graph to its node-weight. 
Currently, this node-weight is a measure of distance from the source article, ie it is equal 
to the number of edges that must be traversed to reach the category node from the article.
'''
from util import wiki_util
import Category_Hierarchy

def build_hierarchy_graph(source_article):
    ''' Returns a Category_Hierarchy object that represents the 
    hierarchy graph of categories originating from the given article. 
    
    TODO: Currently, only the direct parent categories of the article (ie those categories
    at distance = 1) are included in the hierarchy, so need to recurse out through higher
    levels at further distances to build the complete hierarchy graph. '''
    category_to_distance = {}
    direct_categories = wiki_util.query_categories(source_article)
    for category in direct_categories:
        category_to_distance[category] = 1
    hierarchy_graph = Category_Hierarchy.Category_Hierarchy(source_article, category_to_distance)
    return hierarchy_graph