from collections import OrderedDict
from dataset_generation import wikipedia_edits_dataset_mgr
from gensim import corpora, models, similarities
from math import log
from nltk.corpus import stopwords
from nltk.tokenize.regexp import WordPunctTokenizer
from wikipedia import wikipedia_api_util
import math
import nltk
import operator
import pickle

__articletext_usermodel_cache_path__ = 'usermodel_articletext.pkl'

''' TODO 
#def rank_articleBOW_VSM_numedits(candidates, username):
'''

def rank_articleBOW_VSM_gensim(candidates, username):
    ''' Uses gensim to be faster.
    See http://graus.nu/thesis/string-similarity-with-tfidf-and-python/ '''
    
    if len(candidates)==0:
        return {}
    
    # Make corpus
    corpus_docs = []
    user_doc = __get_user_doc__(username)
    corpus_docs.append(user_doc)
    for candidate in candidates:
        candidate_doc = __get_candidate_doc__(candidate)
        corpus_docs.append(candidate_doc)
        
    dictionary = corpora.Dictionary(corpus_docs)
    corpus = MyCorpus(corpus_docs, dictionary)
    tfidf = models.TfidfModel(corpus)
    
    user_bow = dictionary.doc2bow(user_doc)
    tfidf_user = tfidf[user_bow]
    
    scores = {}
    for candidate in candidates:
        clean_cand = __get_candidate_doc__(candidate)
        cand_bow = dictionary.doc2bow(clean_cand)
        tfidf_candidate = tfidf[cand_bow]
        sim = __compare_docs__(tfidf_user, tfidf_candidate, dictionary)
        scores[candidate['article_id']] = sim
    sorted_scores = OrderedDict(sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True))
    return sorted_scores
class MyCorpus(object):
    def __init__(self, corpus_docs, dictionary):
        self.corpus_docs = corpus_docs
        self.dictionary = dictionary
    def __iter__(self):
        for doc in self.corpus_docs:
            yield self.dictionary.doc2bow(doc) 
def __compare_docs__(tfidf1, tfidf2, dictionary):
    index = similarities.MatrixSimilarity([tfidf1],num_features=len(dictionary))
    sim = index[tfidf2]
    #print str(round(sim*100,2))+'% similar'
    return round(sim*100,2)
    
def rank_articleBOW_VSM(candidates, username):
    ''' Ranks each of the given candidates by comparing the text similarity 
    of the Wikipedia article it corresponds to against the Wikipedia articles
    that the given user has edited '''
    
    if len(candidates)==0:
        return {}
    
    scores = {}
    td_matrix = __make_td_matrix__(username, candidates)
    for candidate in candidates:
        candidate_id = candidate['article_id']
        try:
            candidate_score = __compute_sim_for_candidate__(candidate_id, username, td_matrix)
            scores[candidate_id] = candidate_score
        except Exception as e:
            print "Problem computing similarity of candidate "+str(candidate_id), e   
            raise
    sorted_scores = OrderedDict(sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True))
    return sorted_scores

def __make_td_matrix__(username, candidates):
    td_matrix = {}
    
    # Corpus of user doc and candidate docs of ambiguous entity
    corpus_of_BOW_docs = []
    
    # Note that each "document" is a list of tokens
    
    # Make document for user
    user_BOW_doc = __get_user_doc__(username)
    corpus_of_BOW_docs.append(user_BOW_doc)
    
    # Make documents for all candidates
    candidate_BOW_docs = {}
    for candidate in candidates:
        candidate_BOW_doc = __get_candidate_doc__(candidate)
        candidate_BOW_docs[candidate['article_id']] = candidate_BOW_doc
        corpus_of_BOW_docs.append(candidate_BOW_doc)
    
    # Add user doc to matrix (if not already added previously)
    print "Adding user doc to matrix..."
    idf_cache = {} # Cache idf values so don't have to keep recalculating
    td_matrix[username] = {}
    user_len = float(len(user_BOW_doc))
    user_fdist = nltk.FreqDist(user_BOW_doc)
    for term in user_fdist.iterkeys():
        
        tf_user = user_fdist[term] / user_len
        if term in idf_cache:
            idf_user = idf_cache[term]
        else:
            idf_user = __compute_idf__(term, corpus_of_BOW_docs)
            idf_cache[term] = idf_user
            
        td_matrix[username][term] = tf_user * idf_user
    print "User doc added to matrix."
    
    # Add candidates' docs to matrix
    print "Adding candidates to matrix..."
    for candidate_id in candidate_BOW_docs:
        try:
            if candidate_id in td_matrix:
                continue 
                
            candidate_BOW_doc = candidate_BOW_docs[candidate_id]
            candidate_len = float(len(candidate_BOW_doc))
            candidate_fdist = nltk.FreqDist(candidate_BOW_doc)
            if 0==len(candidate_fdist.keys()):
                continue
            
            td_matrix[candidate_id] = {}
            for term in candidate_fdist.iterkeys():
                try:
                    tf_candidate = candidate_fdist[term] / candidate_len
                    if term in idf_cache:
                        idf_candidate = idf_cache[term]
                    else:
                        idf_candidate = __compute_idf__(term, corpus_of_BOW_docs)
                        idf_cache[term] = idf_candidate
                
                    td_matrix[candidate_id][term] = tf_candidate * idf_candidate
                except Exception as term_exception:
                    print "Problem with term "+str(term), term_exception
                    continue
        except Exception as candidate_exception:
            raise
            print "Problem with candidate "+str(candidate_id), candidate_exception
    print "Candidate docs added to matrix."
    
    return td_matrix
    
def __get_user_doc__(username, incorporate_edit_count=False):
    ''' Returns a mapping from BOW of an article (a list of tokens) to number
    of times the given user has made non-trivial edits on that article. '''
    try:
        print "Attempting to load edited article BOW user model..."
        read_model = open(__articletext_usermodel_cache_path__, 'rb')
        user_models = pickle.load(read_model)
    except:
        user_models = {}
    if username in user_models:
        return user_models[username]

    # Model for user doesn't exist yet, so create it
    print "Model for user "+username+" not yet created, so creating and caching..."
    user_model = __create_user_document__(username)
    user_models[username] = user_model
    # and save to file
    write_pkl = open(__articletext_usermodel_cache_path__, 'wb')
    pickle.dump(user_models, write_pkl)
    write_pkl.close()
    return user_model

def __create_user_document__(username):
    ''' Returns a bag of words build from the text content
    on the pages this user has non-trivially edited.
    @return: a list of tokens '''
    
    user_articles = {'I program a lot, internet explorer is my least favorite browser, i prefer chrome':2}
    user_doc = ' '.join(user_articles.keys())
    if True:
        return user_doc
    
    articletext_to_numedits = {}
    
    # get article text for each article user edited and cache it
    # along with the number of times the user edited that page
    articleids_to_numedits = wikipedia_edits_dataset_mgr.get_edits_by_user(username)
    if len(articleids_to_numedits)==0:
        # no edits by user yet, so make sure those 
        # have been fetched and stored in the dataset
        print "No edits by user "+str(username)+\
        " cached yet, so fetching those now and adding to edits dataset..."
        wikipedia_edits_dataset_mgr.build_edits_by_user(username)
        articleids_to_numedits = wikipedia_edits_dataset_mgr.get_edits_by_user(username)
    
    print "Processing edited articles to build user model..."
    progress_count = 1
    progress_finish = len(articleids_to_numedits)
    for article_id in articleids_to_numedits:
        
        if progress_count%10==0:
            print "Added "+str(progress_count)+" articles out of "+str(progress_finish)+" to user model..."
        progress_count = progress_count+1
        
        # get the text of the article's
        article_text = wikipedia_api_util.query_page_content_text(article_id)
        
        # clean the article text 
        cleaned_tokens = __get_clean_doc__(article_text)
        
        # map cleaned text to number of times 
        # that page was edited by the user
        num_edits = articleids_to_numedits[article_id]
        articletext_to_numedits[cleaned_tokens] = num_edits
        
    return articletext_to_numedits
    
def __get_candidate_doc__(wikiminer_candidate):
    ''' Returns a bag of words build from the text content
    on this candidate resource's Wikipedia page. 
    @return: a list of tokens '''
    candidate_text = wikipedia_api_util.query_page_content_text(wikiminer_candidate['article_id'])
    candidate_tokens = __get_clean_doc__(candidate_text)
    return candidate_tokens

def __get_clean_doc__(doc):
    ''' Tokenizes and filters/formats the words in the given document to be used during 
    similarity measurement. This method should be used both when a doc goes into the  
    corpus and when a doc is being compared to another doc for similarity. 
    @return: a list of tokens '''
    stopset = set(stopwords.words('english'))
    stemmer = nltk.PorterStemmer()
    tokens = WordPunctTokenizer().tokenize(doc)
    clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 2]
    final = [stemmer.stem(word) for word in clean]
    return final

def __compute_idf__(term, corpus):
    num_texts_with_term = len([True for token_list in corpus if term.lower()
                               in token_list])

    # tf-idf calc involves multiplying against a tf value less than 0, 
    # so it's important to return a value greater than 1 for consistent
    # scoring. (Multipling two values less than 1 returns a value less
    # than each of them.
    try:
        return 1.0 + log(float(len(corpus)) / num_texts_with_term)
    except ZeroDivisionError:
        return 1.0
    
def __compute_sim_for_candidate__(candidate_id, username, td_matrix):  
    print "Scoring candidate "+str(candidate_id)+"..."
    user_terms = td_matrix[username].copy()
    # Take care not to mutate the original data structures
    # since we're in a loop and need the originals multiple times
    candidate_terms = td_matrix[candidate_id].copy()
    
    # Fill in "gaps" in each map so vectors of the same length can be computed
    for cand_term in candidate_terms:
        if cand_term not in user_terms:
            user_terms[cand_term] = 0.0
    for user_term in user_terms:
        if user_term not in candidate_terms:
            candidate_terms[user_term] = 0.0
            
    # Create vectors from term maps
    v1 = [score for (term, score) in sorted(candidate_terms.items())]
    v2 = [score for (term, score) in sorted(user_terms.items())]    
    
    # Compute similarity amongst documents
    sim_score = __cos_sim__(v1, v2)
    return sim_score
    
def __cos_sim__(a,b):
    return __dot__(a,b) / (__norm__(a) * __norm__(b))
def __dot__(a,b):
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * b[i];
    return sum_val
def __norm__(a):
    ''' Prevents division by 0'''
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * a[i]
    if sum_val==0:
        sum_val=1 # prevent division by 0 in cosine sim calculation
    return math.sqrt(sum_val)