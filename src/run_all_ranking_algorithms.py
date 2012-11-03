from dataset_generation import prompt_and_print, entity_dataset_mgr, \
    crosssite_username_dataset_mgr, pkl_util
from mechanical_turk import unresolved_entities_task
from ranking_algorithms.article_VSM import Article_ContentBOW_VSM, \
    Article_ID_VSM, Article_TitleBOW_VSM
from ranking_algorithms.article_WSD import Article_ContentBOW_WSD
from ranking_algorithms.direct_categories import DirectCategory_ID_VSM, \
    DirectCategory_TitleBOW_VSM
from ranking_algorithms.graph_categories import CategoryGraph_ID_VSM, \
    CategoryGraph_TitleBOW_VSM
from results.candidate_rankings import ResolvedEntity
import random

__resolved_entities_output_str__ = "Candidate resources judged by Mechanical Turkers..."
def  __get_resolved_entities_cache_path__(site):
    return '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/resolved_entities_cache_'+str(site.siteName)+'.pkl'

def get_resolved_entities_cache(site):
    resolved_entities = pkl_util.load_pickle(__resolved_entities_output_str__, 
                                              __get_resolved_entities_cache_path__(site))
    if resolved_entities is None:
        return {}    
    return resolved_entities

def run_all_algorithms():
    
    # Prompt to ask which site's short text entities we want to disambiguate
    try:
        site = prompt_and_print.prompt_for_site()
    except KeyError:
        print "Sorry, that is not a recognized site. Exiting."
        return
    
    # Valid entities and their labels annotated by Mechanical Turk workers
    entities_to_evaluate = entity_dataset_mgr.get_valid_ne_candidates(site)
    entity_judgments = unresolved_entities_task.get_entity_judgements(site)
    if (entities_to_evaluate is None or len(entities_to_evaluate)==0 or 
        entity_judgments is None or len(entity_judgments))==0:
        print "No labeled ambiguous entities + candidates available. Run appropriate scripts first."
        return {}
    
    # Usernames that do not belong to the same individual on the site and
    # Wikipedia and that we'll use as a baseline for no background knowledge
    nonmatch_usernames = crosssite_username_dataset_mgr.get_confirmed_nonmatch_usernames()
    
    # RESLVE algorithms based on articles' page content
    article_contentBowVsm = Article_ContentBOW_VSM()
    article_idVsm = Article_ID_VSM()
    article_titleBowVsm = Article_TitleBOW_VSM()
    
    # RESLVE algorithms based on articles' direct categories
    directCategory_idVsm = DirectCategory_ID_VSM
    directCategory_titleBowVsm = DirectCategory_TitleBOW_VSM
    
    # RESLVE algorithms based on articles' full category hierarchy
    graphCategory_idVsm = CategoryGraph_ID_VSM()
    graphCategory_titleBowVsm = CategoryGraph_TitleBOW_VSM()

    # RESLVE algorithm based on WSD lesk approach
    articleContent_bowWsd = Article_ContentBOW_WSD()
    
    reslve_algorithms = [article_contentBowVsm, article_idVsm, article_titleBowVsm, 
                         directCategory_idVsm, directCategory_titleBowVsm, 
                         graphCategory_idVsm, graphCategory_titleBowVsm, 
                         articleContent_bowWsd]
    
    resolved_entities = []
    for ne_obj in entities_to_evaluate:
        entity_id = ne_obj.get_entity_id()
        if not entity_id in entity_judgments:
            continue # this entity wasn't labeled by a human judge
        
        evaluated_candidates = entity_judgments[entity_id]
        
        # construct a ResolvedEntity object to represent this
        # ambiguous entity and its various candidate rankings
        resolved_entity = ResolvedEntity(ne_obj, evaluated_candidates)   
        resolved_entities.append(resolved_entity)
        
        for rslve_alg in reslve_algorithms:
            
            candidate_titles = ne_obj.get_candidate_titles()
            
            # perform the RESLVE ranking..
            reslve_ranking_user_match = rslve_alg.rank_candidates(candidate_titles, 
                                                                  ne_obj.username)
            
            # perform the same algorithm's ranking again but this time use 
            # a non-match user's interest model as background information, 
            # which according to our hypothesis should provide less relevant
            # semantic background knowledge and thus have lower performance
            random.shuffle(nonmatch_usernames)
            random_nonmatch_username = nonmatch_usernames[0]
            reslve_ranking_user_nonmatch = rslve_alg.rank_candidates(candidate_titles, 
                                                                     random_nonmatch_username)
            
            resolved_entity.add_reslve_ranking(rslve_alg.alg_id, 
                                               reslve_ranking_user_match, reslve_ranking_user_nonmatch)

    # Cache resolved entities
    pkl_util.write_pickle(__resolved_entities_output_str__, resolved_entities, __get_resolved_entities_cache_path__(site))

run_all_algorithms()