from collections import OrderedDict
from gensim import similarities, corpora, models
from math import log
from ranking_algorithms.reslve_algorithm import RESLVE_Algorithm
import math
import nltk
import operator

####### The VSM algorithm "Interface" #######
class VSM_Algorithm(RESLVE_Algorithm):
    ''' VSM based algorithm '''
    
    def get_article_representation(self, article_title):
        ''' Should be implemented by subclasses '''
        raise Exception("get_article_representation needs to be implemented "+str(self.alg_type))
    
    def rank_candidates(self, candidate_objs, username, use_gensim=True):
        # use gensim because it's faster
        candidate_titles = candidate_objs.keys()
        if use_gensim:
            return self.__rank_VSM_gensim__(candidate_titles, username)
        else:
            return self.__rank_VSM_tdmatrix__(candidate_titles, username)
        
    def __get_candidate_doc__(self, candidate_title):
        ''' Returns a representation based on
        on this candidate resource's Wikipedia page. 
        @return: a list of tokens '''
        return self.get_article_representation(candidate_title)
    
    ######### Computing similarity using gensim:
    def __rank_VSM_gensim__(self, candidate_titles, username):
        ''' Uses gensim to be faster.
        See http://graus.nu/thesis/string-similarity-with-tfidf-and-python/ '''
        if len(candidate_titles)==0:
            return {}
        
        # Make corpus
        corpus_docs = []
        user_doc = self.get_user_doc(username)
        corpus_docs.append(user_doc)
        for candidate_title in candidate_titles:
            candidate_doc = self.__get_candidate_doc__(candidate_title)
            corpus_docs.append(candidate_doc)
            
        dictionary = corpora.Dictionary(corpus_docs)
        corpus = DocumentCorpus(corpus_docs, dictionary)
        tfidf = models.TfidfModel(corpus)
        
        user_bow = dictionary.doc2bow(user_doc)
        tfidf_user = tfidf[user_bow]
        
        scores = {}
        for candidate_title in candidate_titles:
            clean_cand = self.__get_candidate_doc__(candidate_title)
            cand_bow = dictionary.doc2bow(clean_cand)
            tfidf_candidate = tfidf[cand_bow]
            sim = self.__compare_docs__(tfidf_user, tfidf_candidate, dictionary)
            scores[candidate_title] = sim
        sorted_scores = OrderedDict(sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True))
        return sorted_scores
    def __compare_docs__(self, tfidf1, tfidf2, dictionary):
        index = similarities.MatrixSimilarity([tfidf1],num_features=len(dictionary))
        sim = index[tfidf2]
        #print str(round(sim*100,2))+'% similar'
        return round(sim*100,2)
        
    ######### Computing similarity by implementing own inverted term doc frequency matrix:
    def __rank_VSM_tdmatrix__(self, candidate_titles, username):
        ''' Ranks each of the given candidates by comparing the text similarity 
        of the Wikipedia article it corresponds to against the Wikipedia articles
        that the given user has edited '''
        
        if len(candidate_titles)==0:
            return {}
        
        scores = {}
        td_matrix = self.__make_td_matrix__(username, candidate_titles)
        for candidate_title in candidate_titles:
            try:
                candidate_score = self.__compute_sim_for_candidate__(candidate_title, username, td_matrix)
                scores[candidate_title] = candidate_score
            except Exception as e:
                print "Problem computing similarity of candidate "+str(candidate_title), e   
                raise
        sorted_scores = OrderedDict(sorted(scores.iteritems(), key=operator.itemgetter(1), reverse=True))
        return sorted_scores
    def __make_td_matrix__(self, username, candidate_titles):
        td_matrix = {}
        
        # Corpus of user doc and candidate docs of ambiguous entity
        corpus_of_BOW_docs = []
        
        # Note that each "document" is a list of tokens
        
        # Make document for user
        user_BOW_doc = self.get_user_doc(username)
        corpus_of_BOW_docs.append(user_BOW_doc)
        
        # Make documents for all candidates
        candidate_BOW_docs = {}
        for candidate_title in candidate_titles:
            candidate_BOW_doc = self.__get_candidate_doc__(candidate_title)
            candidate_BOW_docs[candidate_title] = candidate_BOW_doc
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
                idf_user = self.__compute_idf__(term, corpus_of_BOW_docs)
                idf_cache[term] = idf_user
                
            td_matrix[username][term] = tf_user * idf_user
        print "User doc added to matrix."
        
        # Add candidates' docs to matrix
        print "Adding candidates to matrix..."
        for candidate_title in candidate_BOW_docs:
            try:
                if candidate_title in td_matrix:
                    continue 
                    
                candidate_BOW_doc = candidate_BOW_docs[candidate_title]
                candidate_len = float(len(candidate_BOW_doc))
                candidate_fdist = nltk.FreqDist(candidate_BOW_doc)
                td_matrix[candidate_title] = {}
                
                if 0==len(candidate_fdist.keys()):
                    continue
                
                for term in candidate_fdist.iterkeys():
                    try:
                        tf_candidate = candidate_fdist[term] / candidate_len
                        if term in idf_cache:
                            idf_candidate = idf_cache[term]
                        else:
                            idf_candidate = self.__compute_idf__(term, corpus_of_BOW_docs)
                            idf_cache[term] = idf_candidate
                    
                        td_matrix[candidate_title][term] = tf_candidate * idf_candidate
                    except Exception as term_exception:
                        print "Problem with term "+str(term), term_exception
                        continue
            except Exception as candidate_exception:
                raise
                print "Problem with candidate "+str(candidate_title), candidate_exception
        print "Candidate docs added to matrix."
        return td_matrix
    def __compute_idf__(self, term, corpus):
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
    def __compute_sim_for_candidate__(self, candidate_title, username, td_matrix):  
        print "Scoring candidate "+str(candidate_title)+"..."
        user_terms = td_matrix[username].copy()
        # Take care not to mutate the original data structures
        # since we're in a loop and need the originals multiple times
        candidate_terms = td_matrix[candidate_title].copy()
        
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
        sim_score = self.__cos_sim__(v1, v2)
        return sim_score
    def __cos_sim__(self, a,b):
        return self.__dot__(a,b) / (self.__norm__(a) * self.__norm__(b))
    def __dot__(self, a,b):
        n = len(a)
        sum_val = 0
        for i in xrange(n):
            sum_val += a[i] * b[i];
        return sum_val
    def __norm__(self, a):
        ''' Prevents division by 0'''
        n = len(a)
        sum_val = 0
        for i in xrange(n):
            sum_val += a[i] * a[i]
        if sum_val==0:
            sum_val=1 # prevent division by 0 in cosine sim calculation
        return math.sqrt(sum_val)
    
class DocumentCorpus(object):
    def __init__(self, corpus_docs, dictionary):
        self.corpus_docs = corpus_docs
        self.dictionary = dictionary
    def __iter__(self):
        for doc in self.corpus_docs:
            yield self.dictionary.doc2bow(doc) 