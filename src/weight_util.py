import math
import wiki_fetch_util

def make_candidate_vectors(all_candidates):
    candidate_vectors = {}
    
    category_idfs = compute_idfs(all_candidates)
    for candidate in all_candidates:
        weighted_vector = make_weighted_vector(candidate, category_idfs)
        candidate_vectors[candidate['article_id']] = weighted_vector
        
    return candidate_vectors

def make_weighted_vector(candidate, category_idfs):
    category_to_weight = {}
    cats = wiki_fetch_util.fetch_categories(candidate['article_id'])
    for category in cats:
        weight = calculate_candidatecat_weight(category, category_idfs)
        category_to_weight[category] = weight
    return category_to_weight

def compute_idfs(all_candidates):
    
    # mapping of category -> candidates belonging to that category
    category_to_candidates_map = {}
    
    for candidate in all_candidates:
        candidate_categories = wiki_fetch_util.fetch_categories(candidate['article_id'])
        for category in candidate_categories:
            if category in category_to_candidates_map:
                cand_list = category_to_candidates_map[category]
            else:
                cand_list = []
            cand_list.append(candidate)    
            
            category_to_candidates_map[category] = cand_list
    
    # mapping of category -> idf value        
    category_idfs = {}
    N = len(all_candidates)
    for category_i in category_to_candidates_map:
        df_i = len(category_to_candidates_map[category_i])
        idf_i = math.log(N / df_i, 10)
        category_idfs[category_i] = idf_i
        
    return category_idfs

def calculate_candidatecat_weight(category, category_idfs):
    breadth_tf = 1
    #breadth_tf = breadth_tf / len(cats) # normalize? 
    breadth_idf = category_idfs[category]
    tf_idf = breadth_tf * breadth_idf
    return tf_idf
