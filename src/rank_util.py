from numpy.lib.scimath import sqrt
from spreadsheet_labels import USERNAME_COLUMN, PAGEID_COLUMN, CATEGORIES_COLUMN, \
    NUMEDITS_COLUMN
from util import wiki_util
import Candidate
import Candidate_Vector
import User
import User_Vector
import category_hierarchy_builder
import csv
import math
import pickle
import pprint

def rank_candidates(user_obj, candidate_objs):
    
    # construct dictionary of all categories (user categories + all candidates' categories)
    category_dictionary = build_category_dictionary(user_obj, candidate_objs)
    
    # get the total number of edits ever made by any user on the categories in 
    # the dictionary so that we can compute the category edits idfs up front
    try:
        ae = open('all_edits.pkl', 'rb')
        cat_to_total_edits = pickle.load(ae)
    except:
        cat_to_total_edits = map_category_to_total_edits(user_obj, candidate_objs)
        ae = open('all_edits.pkl', 'wb')
        pickle.dump(cat_to_total_edits, ae)
        ae.close()
    category_edit_idfs = compute_category_edits_idf(category_dictionary, cat_to_total_edits)
    
    # construct user vector
    user_vector = construct_user_vector(user_obj, category_dictionary, category_edit_idfs, candidate_objs)
    
    # construct candidate vectors and compute similarity between each and user vector
    candidate_scores = {}
    for candidate_obj in candidate_objs:
        candidate_vector = construct_candidate_vector(candidate_obj, category_dictionary)
        
        # compute similarity score between q and this document
        score = sim(candidate_vector, user_vector)
        candidate_scores[candidate_obj.get_candidateID()] = score
    
    # sort by decreasing score
    sorted_candidate_scores = {}
    sorted_candidates = sorted(candidate_scores, key=candidate_scores.get, reverse=True)
    for sc in sorted_candidates:
        sorted_candidate_scores[sc] = candidate_scores[sc]
    return sorted_candidate_scores

def construct_user_obj(username):
    
    cat_to_user_edits = {}
    hierarchy_to_user_edits = {}
    
    edits_file = open('pickles/edits.pkl', 'rb')
    edits = pickle.load(edits_file)
    user_edits = edits[username]
    print user_edits
    for articleID_entry in user_edits.keys():
        num_edits_entry = user_edits[articleID_entry]
  
        '''
    edits_reader = csv.reader(open('spreadsheets/edits.csv', 'rb'))
   
    edits_headers = edits_reader.next()
    username_index = edits_headers.index(USERNAME_COLUMN)
    articleID_index = edits_headers.index(PAGEID_COLUMN)
    num_edits_index = edits_headers.index(NUMEDITS_COLUMN)
    
    while True:
        try:
            row = edits_reader.next()
        except StopIteration:
            break
        except Exception:
            continue
        
        if username != row[username_index]:
            continue
        
        articleID_entry = row[articleID_index]
        num_edits_entry = int(row[num_edits_index])
        '''  

        category_hierarchy = category_hierarchy_builder.build_hierarchy_graph(articleID_entry)
        hierarchy_to_user_edits[category_hierarchy] = num_edits_entry
        
        categories_list = category_hierarchy.get_category_to_distance().keys()

        for cat in categories_list:
            
            # map category -> number of edits that the user 
            # made on pages belonging to that category
            if cat in cat_to_user_edits:
                num_user_edits = cat_to_user_edits[cat]
            else: 
                num_user_edits = 0
            num_user_edits = num_user_edits + num_edits_entry
            cat_to_user_edits[cat] = num_user_edits
            
    user_obj = User.User(username, hierarchy_to_user_edits, cat_to_user_edits)      
    return user_obj

def construct_candidate_obj_from_wikiminer_candidate(candidate):
    
    # Exract info stored in wikiminer object
    candidate_URI = candidate['article_id']
    title = candidate['title']
    dbpedia_uri = candidate['dbpedia_uri']
    wikiminer_weight = candidate['weight']
    
    # Build category hierarchy graph
    hierarchy = category_hierarchy_builder.build_hierarchy_graph(candidate_URI)
    
    # Create Candidate object
    candidate_obj = Candidate.Candidate(candidate_URI, title, dbpedia_uri, wikiminer_weight, hierarchy)
    return candidate_obj
    
def build_category_dictionary(query, all_docs):
    ''' Create a corpus of categories, ie a set of all categories 
    found in the query's or any candidate's category hierarchy. 
    @param query: a User object
    @param all_docs: a list of all the Candidate objects
    '''
    category_set = set()
    
    # get categories in query's category hierarchy
    query_categories = query.get_categories_to_num_edits().keys()
    category_set.update(query_categories)
    for doc in all_docs:
        # get categories in doc's category hierarchy
        doc_categories = doc.get_category_list()
        category_set.update(doc_categories)
        
    return category_set    

def map_category_to_total_edits(user, all_candidates):
    category_to_all_edits_num = {}
    user_hierarchies = user.get_category_hierarchies()
    for user_h in user_hierarchies:
        category_to_all_edits_num = __map_new_category_total__(user_h, category_to_all_edits_num)
    for candidate in all_candidates:
        cand_h = candidate.get_category_hierarchy()
        category_to_all_edits_num = __map_new_category_total__(cand_h, category_to_all_edits_num)
    return category_to_all_edits_num
def __map_new_category_total__(hierarchy, category_to_all_edits_num):
    for category in hierarchy.get_category_list():
        if category in category_to_all_edits_num:
            cat_num = category_to_all_edits_num[category]
        else:
            cat_num = 0
        cat_num = cat_num+wiki_util.query_hierarchy_edits(hierarchy)
        category_to_all_edits_num[category] = cat_num
    return category_to_all_edits_num

def map_category_to_candidates(all_candidates):
    ''' @param param: all_candidates A list of Candidate objects
        @return: a mapping of category -> Candidates that have that category in their hierarchy '''
    category_to_candidates_map = {}
    for candidate_obj in all_candidates:
        
        candidate_categories = candidate_obj.get_category_list()
        for category in candidate_categories:
            if category in category_to_candidates_map:
                cand_list = category_to_candidates_map[category]
            else:
                cand_list = []
            cand_list.append(candidate_obj)    
            
            category_to_candidates_map[category] = cand_list
    return category_to_candidates_map
    
def construct_candidate_vector(d, category_dictionary):
    ''' Returns a Category_Vector object 
    representing a weighted category vector
    for the given document d, which should
    be a Candidate object '''
    
    ''' w_c,d= normalized(tf_c,d) = tf_c,d / || tf_c,d || '''
    
    candidate_URI = d.get_candidateID()
    category_hierarchy = d.get_category_hierarchy()
    candidate_categories = d.get_category_list()
    
    # Compute Euclidean length of candidate d
    squares_sum = 0
    for candidate_category in candidate_categories:
        squared = category_hierarchy.get_category_distance(candidate_category) ** 2
        squares_sum = squares_sum + squared
    eucl_length_d = sqrt(squares_sum)
    if eucl_length_d==0:
        eucl_length_d = 1
    
    # Compute weight for each category in corpus
    weighted_vector = {}
    for category in category_dictionary:
        
        # tf_c,d reflects the position of category c in category hierarchy 
        # graph of candidate d.
        # If the category is not in the candidate's hierarchy, the tf_c,d value
        # is simply 0, otherwise the tf_c,d value equals the number of steps out
        # the category node lies from the article source in the hierarchy graph 
        tf_cd = 0
        if category in category_hierarchy.get_category_to_distance():
            tf_cd = category_hierarchy.get_category_distance(category)
            
        w_cd = float(tf_cd) / float(eucl_length_d)
        weighted_vector[category] = w_cd
    
    candidate_vector = Candidate_Vector.Candidate_Vector(candidate_URI, weighted_vector)
    return candidate_vector  

def construct_user_vector(q, category_dictionary, category_edit_idfs, all_candidate_objs):
    ''' Returns a User_Vector object 
    representing a weighted category vector
    for the given query q, which should
    be a User object '''
    
    # Composite weight incorporating both info about the distance of a category 
    # from the source article (tf-idf)c,q and info about the number of edits the 
    # user made articles belonging to that category (tf-idf)c,e,q
    ''' w_c,q = (tf-idf)c,q * (tf-idf)c,e,q
              = (tf_c,q * idf_c) * (tf_c,e,q * idf_c,e) '''
    
    # get mapping from each category in the user's category hierarchies to 
    # the number of times that user edited article(s) within that category
    category_to_num_edits = q.get_categories_to_num_edits()
    
    # get mapping from each category to the candidates that have that category in their hierarchy
    category_to_candidates_map = map_category_to_candidates(all_candidate_objs)
    
    # Compute weight for each category in corpus
    weighted_vector = {}
    for category in category_dictionary:
        
        # tfc,q reflects the position of category c in full category hierarchy 
        # of user model q.
        # If the category is not in the hierarchy of any of the user's edited 
        # articles, the tf_c,q value is simply 0, otherwise the tf_c,q value 
        # equals the minimum number of steps out that the category node lies 
        # from the article source in any of the user's hierarchy graphs
        tf_cq = 0
        try:
            min_dist = q.get_shortest_path(category)
            if min_dist > -1:
                tf_cq = min_dist
        except:
            tf_cq = 0
            
        #idf_c = reflects how common category is, ie how many articles it is associated with 
        idf_c = compute_category_position_idf(category, all_candidate_objs, category_to_candidates_map)
        
        # tfc,e,q = the number of times the user has edited articles belonging to category c
        if category in category_to_num_edits:
            tf_ceq = category_to_num_edits[category]
        else:
            tf_ceq = 0
        
        # idf_ec = reflects how commonly the category's associated articles are edited
        idf_ec = category_edit_idfs[category]
        
        w_cq = (tf_cq * idf_c) * (tf_ceq * idf_ec)
        weighted_vector[category] = w_cq
        
    username = q.get_username()
    user_vector = User_Vector.User_Vector(username, weighted_vector)
    return user_vector  

def compute_category_position_idf(category, all_candidates, category_to_candidates_map):
    ''' Returns an idf value for the given category that reflects how 
    discriminating the topic of that category is, ie categories that are more
    common and associated with many articles are less discriminating and 
    indicative of a user's individual interests. '''
    
    # total number of candidates
    N = len(all_candidates)
    
    # number of candidates with category 
    # hierarchies that contain category c
    if category in category_to_candidates_map:
        candidates_with_category = category_to_candidates_map[category]
    else:
        # insert one entry, the empty string, so that list's length 
        # isn't 0, which would cause a division by zero error
        candidates_with_category = ['']
    df_c = len(candidates_with_category)
    
    idf_c = math.log(N / df_c, 10)
    return idf_c
    
def compute_category_edits_idf(category_dictionary, cat_to_total_edits):
    ''' Returns a mapping from each category in the dictionary to an 
    idf value that reflects how "discriminating" the revision history
    of articles in that category are, ie articles that many editors edit 
    aren't as discriminating and indicative of user's individual interests. '''
    idfs = {}
    
    # total number of edits made on Wikipedia
    total_edits = wiki_util.query_total_edits()
    if len(total_edits)==0:
        M = 0
    else:
        M = int(total_edits[0])
        
    for category in category_dictionary:
        # number of edits made to the articles from which 
        # category c originates in the user's hierarchies 
        df_ec = cat_to_total_edits[category]
        idf_ec = math.log(M / df_ec, 10)
        idfs[category] = idf_ec
        
    return idfs

def sim(d_j, q):
    ''' Computes the similarity score between the given 
    document (candidate) vector, d_j, and the query 
    (user model) vector, q '''
    
    ''' Using cosine similarity, which is the sum of the 
    products of the weights of matched categories:
    sim(d_j, q) = Summation (w_i,j * w_i,q) for all categories i in C, 
    where C is the category corpus, ie the set of all categories found 
    in any candidate or query's hierarchy '''
    
    candidate_weighted_vector = d_j.get_weighted_vector()
    user_weighted_vector = q.get_weighted_vector()
    sum_val = 0
    for category in user_weighted_vector:
        w_ij = candidate_weighted_vector[category] 
        w_iq = user_weighted_vector[category]
        sum_val = sum_val + (w_ij * w_iq)
    print "sum val:"+str(sum_val)
    
    print "comparing to jaccard"
    jacc = jaccard_similarity_weighted_vectors(d_j, q)
    print jacc
        
    print "comparing to cosine function"
    #cossim = cosine_similarity(d_j.get_weighted_vector(), q.get_weighted_vector())
    #print cossim
        
    return sum_val


def jaccard_similarity_weighted_vectors(d_j, q):
    ''' Computes similarity based on binary absence or presence 
    of terms rather than the frequency of terms. 
    @param d_j: "document" (candidate) weighted vector of type Candidate_Vector
    @param q: "query" (user model) weighted vector of type User_Vector
    '''
    
    # Get list of categories in candidate's weighted vector that have non-zero weights
    dj_vector = d_j.get_weighted_vector()
    dj_categories = []
    for djcand in dj_vector:
        if dj_vector[djcand]>0:
            dj_categories.append(djcand)
            
    q_vector = q.get_weighted_vector()
    q_categories = []
    for qcand in q_vector:
        if q_vector[qcand]!=0:
            q_categories.append(qcand)     
            
    jacc = jaccard_similarity(dj_categories, q_categories)
    return jacc   
    
def jaccard_similarity(doc1_words, doc2_words):
    ''' Computes jaccard similarity between two given lists. Each list
    should be a list of the words in that document.
    See http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/tani.html '''
    intersection = [common_word for common_word in doc1_words if common_word in doc2_words]
    return float(len(intersection))/(len(doc1_words) + len(doc2_words) - len(intersection))    

def dot(a,b):
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * b[i];
    return sum_val

def norm(a):
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * a[i]
    return math.sqrt(sum_val)

def cossim(a,b):
    return dot(a,b) / (norm(a) * norm(b))
  
# See http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/cos.html
def cosine_similarity(doc_vector1, doc_vector2):
    # Calculate numerator of cosine similarity
    dot = [doc_vector1[i] * doc_vector2[i] for i in range(len(doc_vector1))]
  
    # Normalize the first vector
    sum_vector1 = 0.0
    print range(len(doc_vector1))
    sum_vector1 += sum_vector1 + (doc_vector1[i]*doc_vector1[i] for i in range(len(doc_vector1)))
    norm_vector1 = sqrt(sum_vector1)
  
    # Normalize the second vector
    sum_vector2 = 0.0
    sum_vector2 += sum_vector2 + (doc_vector2[i]*doc_vector2[i] for i in range(len(doc_vector2)))
    norm_vector2 = sqrt(sum_vector2)
  
    return (dot/(norm_vector1*norm_vector2))
