from collections import OrderedDict
import operator
import random

class ResolvedEntity():
    ''' Represents an ambiguous named entity whose candidate resources have been resolved and
    ranked using various strategies (Turker judgment, baseline toolkits, RESLVE algorithms) '''
        
    def __init__(self, ne_obj, labeled_candidates):
        ''' @param labeled_candidates: { candidate title -> (num times labeled as correct, num times labelled as incorrect) } '''
        self.ne_obj = ne_obj
        self.labeled_candidates = labeled_candidates
        self.reslve_rankings = {}
        
    def add_reslve_ranking(self, alg_id, ranking_usermatch, ranking_user_nonmatch):
        ''' 
        @param ranking_usermatch: a mapping from candidate title -> score according 
        to the running the RESLVE algorithm with the given id and giving it the 
        usermodel of the person who authored the entity
        @param ranking_user_nonmatch: a mapping from candidate title -> score according 
        to the running the RESLVE algorithm with the given id and giving it the 
        usermodel of the person who DID NOT author the entity '''
        self.reslve_rankings[alg_id] = (ranking_usermatch, ranking_user_nonmatch)
        
    ''' Tests whether various rankings are correct, ie
        whether they agree with the human judges) '''
    def is_reslve_correct(self, alg_id):
        return self.__is_correct__(self.get_top_candidates_reslve(alg_id, True))
    def is_baseline_reslve_nonmatch_correct(self, alg_id):
        return self.__is_correct__(self.get_top_candidates_reslve(alg_id, False))
    def is_baseline_wikiminer_correct(self):
        return self.__is_correct__(self.get_top_candidates_baseline_wikiminer())
    def is_baseline_dbpedia_correct(self):
        return self.__is_correct__(self.get_top_candidates_baseline_dbpedia())
    def is_baseline_random_correct(self):
        return self.__is_correct__(self.get_top_candidates_baseline_random())
    def is_goldstandard_correct(self):
        # Just a sanity test; should always be correct
        return self.__is_correct__(self.get_unanimous_candidates_goldstandard())
    def __is_correct__(self, top_candidates):
        gold_candidates = self.get_unanimous_candidates_goldstandard()
        for top_cand in top_candidates:
            if top_cand in gold_candidates:
                return True
        return False
        
    def get_unanimous_candidates_goldstandard(self):
        ''' Returns the candidates that workers agreed upon as 
        relevant for this entity. Currently, requiring all workers
        to unanimously agree (ie must have all turkers label a candidate
        as relevant and no turkers label it as not relevant). '''
        unanimous_candidates = []
        for candidate_title in self.labeled_candidates:
            judgment = self.labeled_candidates[candidate_title]
            num_true = judgment[0]
            num_false = judgment[1]
            if num_true>0 and num_false==0:
                unanimous_candidates.append(candidate_title)
        return unanimous_candidates

    def get_top_candidates_reslve(self, alg_id, match_or_nonmatch):
        ''' @param match_or_nonmatch: True if RESLVE algorithm that uses
        matching user's interest model, False if RESLVE algorithm that uses
        random non-matching user's interest model that serves as a baseline '''
        try:
            # reslve ranking is a tuple (matching user model, nonmatching usermodel baseline)
            if match_or_nonmatch:
                tuple_index = 0
            else:
                tuple_index = 1
            cand_score_map = self.reslve_rankings[alg_id][tuple_index]
        except:
            cand_score_map = {}
        reslve_top = self.__get_top_candidates__(cand_score_map)
        if cand_score_map.get(reslve_top[0]) > 0:
            return reslve_top
        # reslve failed to assign a score so choose wikipedia's or dbpedia's
        # top ranked candidate, depending on which service has higher probability
        best_service_top = self.get_most_confident_baseline_service()
        return [best_service_top] # expects a list to be returned
    
    def get_top_candidates_baseline_random(self):
        ''' From the ambiguous entity's set of candidate resources, randomly select one. '''
        candidates = self.ne_obj.get_candidate_titles()[:] # copy (list slicing)
        if len(candidates)==0:
            return []
        random.shuffle(candidates)
        return [candidates[0]]
    
    ''' Rankings from Wikipedia Miner and DBPedia Spotlight are dict of candidate title -> CandidateResource. 
    Need to pull out the score from those CandidateResource objects and sort according to that. '''
    def get_top_candidates_baseline_wikiminer(self):
        return self.__get_top_candidates_baseline_service__(self.ne_obj.wikipedia_miner_ranking)
    def get_top_candidates_baseline_dbpedia(self):
        return self.__get_top_candidates_baseline_service__(self.ne_obj.dbpedia_spotlight_ranking)
    def __get_top_candidates_baseline_service__(self, cand_obj_ranking):
        service_ranked_scores = self.__get_baseline_service_candidate_scores__(cand_obj_ranking)
        return self.__get_top_candidates__(service_ranked_scores)        
    def __get_baseline_service_candidate_scores__(self, service_ranked_objs):
        '''@param service_ranked_objs:  cand_title -> CandidateResource '''
        service_ranked_scores = {}
        for cand_title in service_ranked_objs:
            cand_score = service_ranked_objs[cand_title].get_score()
            service_ranked_scores[cand_title] = cand_score        
        return service_ranked_scores
    
    def get_most_confident_baseline_service(self):
        wikiminer_ranking = self.ne_obj.wikipedia_miner_ranking
        dbpedia_ranking = self.ne_obj.dbpedia_spotlight_ranking        
        if len(wikiminer_ranking)==0:
            return self.get_top_candidates_baseline_dbpedia()[0]
        if len(dbpedia_ranking)==0:
            return self.get_top_candidates_baseline_wikiminer()[0]
            
        # they can't both be empty or else we wouldn't even be analyzing
        # this entity, so the fact we reached this point means they both
        # have a ranking and we want to select the top ranked candidate
        # between the two services with the highest probability..
        
        wikiminer_cand_scores = self.__get_baseline_service_candidate_scores__(wikiminer_ranking)
        sorted_wikiminer = self.__get_sorted_candidate_scores__(wikiminer_cand_scores)
        wikiminer_top_cand_title = sorted_wikiminer.keys()[0]
        top_wikiminer_score = sorted_wikiminer[wikiminer_top_cand_title]
        
        dbpedia_cand_scores = self.__get_baseline_service_candidate_scores__(dbpedia_ranking)
        sorted_dbpedia = self.__get_sorted_candidate_scores__(dbpedia_cand_scores)
        dbpedia_top_cand_title = sorted_dbpedia.keys()[0]
        top_dbpedia_score = sorted_dbpedia[dbpedia_top_cand_title]
        
        if top_wikiminer_score>=1.0 or top_dbpedia_score>=1.0:
            # they're supposed to be probabilities, so this should not happen..
            raise
        
        if top_wikiminer_score > top_dbpedia_score:
            return wikiminer_top_cand_title
        elif top_dbpedia_score > top_wikiminer_score:
            return dbpedia_top_cand_title
        else:
            # they're equally confident so select one at random..
            both = [wikiminer_top_cand_title, dbpedia_top_cand_title]
            random.shuffle(both)
            return both[0]
            
    def __get_top_candidates__(self, candidate_scores):
        ''' Returns the candidate with the highest score in the given map. 
        If more than one candidate ties with the same score, returns them all. '''
        top_candidates = []
        if len(candidate_scores)==0:
            return top_candidates
        candidate_scores = self.__get_sorted_candidate_scores__(candidate_scores)
        top_score = candidate_scores.items()[0][1]
        for candidate_title in candidate_scores:
            candidate_score = candidate_scores[candidate_title]
            if candidate_score>=top_score:
                # a tie with multiple candidates having same sim score
                top_candidates.append(candidate_title)
        return top_candidates
    def __get_sorted_candidate_scores__(self, candidate_scores):
        if len(candidate_scores)==0:
            return {}
        if not isinstance(candidate_scores, OrderedDict):
            # sort scores
            candidate_scores = OrderedDict(sorted(candidate_scores.iteritems(), key=operator.itemgetter(1), reverse=True))
        return candidate_scores
