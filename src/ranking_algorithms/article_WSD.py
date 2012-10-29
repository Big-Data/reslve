''' 
Lesk based algorithm that selects the most frequent sense of a named entity across all the user's docs.
Ranks candidates of an ambiguous entity using the following WSD approach: 
- Create a mapping that will map each candidate to its frequency as top candidate, i.e.,
  { candidate -> number of times that candidate has the highest probability in a disambiguation ranking }
- Search all articles in the user's edit history model for occurrences
  of the ambiguous entity. 
- For each occurrence, use named_entity_finder to disambiguate it. 
- Take that ranking's top candidate (the candidate with the highest probability) and
  increment that candidate's frequency in the mapping.
- After completing this for all occurrences of the entity in all articles, sort the
  mapping in descending order according to a candidate's frequency value and choose 
  the candidate with the highest frequency as our top candidate. 
'''
from ranking_algorithms.reslve_algorithm import RESLVE_Algorithm
from wikipedia import wikipedia_api_util
import Ambiguous_Entity
import named_entity_finder
import text_util

user_articles_NE_cands_cache_path__ = '/Users/elizabethmurnane/git/reslve/data/pickles/user_articles_NE_cands.pkl'    

class Article_ContentBOW_WSD(RESLVE_Algorithm):
    ''' An algorithm that searches a user's edited articles' content for a named entity
    in order to find the one that is ranked at the top the most frequently '''
    
    def __init__(self):
        RESLVE_Algorithm.__init__(self, "article content WSD", "articleContent-WSD")

    def get_article_representation(self, article_title, include_headers=False):
        ''' Returns a list wrapping the string that contains the content of this article's page '''
        article_text = wikipedia_api_util.query_page_content_text(article_title)
        return [article_text]
    
    #def rank_candidates_for_entity_incorporate_editnum(entity_obj):
    #   top_cand_freq = rank_candidates_for_entity(entity_obj, True)
        
    def rank_candidates_for_entity(self, entity_str, username, candidates, incorporate_editnum=False):
        
        # create map of candidate -> frequency appears as top ranked candidate
        top_cand_freq = {}
        
        # get list of strings of user's edited articles
        user_doc = self.get_user_doc(username)
        print "Successfully loaded or created user model based on text in user's edited articles"
        
        # initialize map with entity's candidate resources
        for candidate_title in candidates:
            top_cand_freq[candidate_title] = 0
        
        for article_text in user_doc:
            try:
                clean_entity_str = text_util.get_clean_doc(entity_str)
                clean_article_text = text_util.get_clean_doc(article_text)
                if not clean_entity_str in clean_article_text:
                    continue # entity not in this article
                
                if incorporate_editnum:
                    factor = user_doc[article_text]
                else:
                    factor = 1
                
                # have to do sentence at a time or else breaks toolkits
                sentences = text_util.get_sentences(article_text)
                for sentence in sentences:
                    clean_sentence = text_util.get_clean_doc(sentence)
                    if not clean_entity_str in clean_sentence:
                        continue # entity not in this sentence
 
                    cands = __find_best_candidates_for_entity__(entity_str, clean_entity_str, sentence)
                    if cands is None or len(cands)==0:
                        # tookits unable to detect entity in this sentence at all
                        # or couldn't find any candidates for the entity
                        continue
                    
                    # for each detected entity that matches the one we're searching for, 
                    # get its top candidate and update that candidate's entry in the map 
                    ranked_cands = Ambiguous_Entity.sort_CandidateResources(cands.values())
                    for rc in ranked_cands:
                        cand_title = rc.title
                        if cand_title in top_cand_freq:
                            # this is the highest ranked of the candidates we need to resolve
                            # (might be that ambiguous entity goes to candidates -> c1, c2, c3
                            # and user doc disambiguation maps entity to -> c4, c3, c2, in which case
                            # we need to keep iterating through ranked_cands until encounter one of 
                            # the ambiguous entities candidates, ie here c3)
                            top_cand_freq[cand_title] = top_cand_freq[cand_title] + factor
                            break
            except Exception as e:
                raise
                print "Unexpected exception ", e
                continue
        return top_cand_freq
 
def __find_best_candidates_for_entity__(entity_str, clean_entity_str, sentence): 
    entity_text_to_candidates = named_entity_finder.find_ne_to_candidates(sentence)
    if entity_str in entity_text_to_candidates:
        return entity_text_to_candidates[entity_str]
    if clean_entity_str in entity_text_to_candidates:
        return entity_text_to_candidates[clean_entity_str]

    # clean the detected entities and see if the one
    # we're looking to resolve matches any of those
    backup_cands = None
    for detected_entity in entity_text_to_candidates:
        clean_detected = text_util.get_clean_doc(detected_entity)
        if clean_entity_str==clean_detected:
            return entity_text_to_candidates[detected_entity]

        if clean_entity_str in clean_detected:
            # let exact match take priority but a detected entity
            # containing the surface form can be a backup
            backup_cands = entity_text_to_candidates[detected_entity]
    return backup_cands