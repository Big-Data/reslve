from dataset_generation import prompt_and_print, entity_dataset_mgr
from mechanical_turk import unresolved_entities_task
from ranking_algorithms.article_VSM import Article_ContentBOW_VSM, \
    Article_ID_VSM, Article_TitleBOW_VSM
from ranking_algorithms.article_WSD import Article_ContentBOW_WSD
from ranking_algorithms.direct_categories import DirectCategory_ID_VSM, \
    DirectCategory_TitleBOW_VSM
from ranking_algorithms.graph_categories import CategoryGraph_ID_VSM, \
    CategoryGraph_TitleBOW_VSM

def run_all_algorithms():
    
    site = prompt_and_print.prompt_for_site()
    entities_to_evaluate = entity_dataset_mgr.get_ne_candidates_to_evaluate_mturk(site)
    entity_judgments = unresolved_entities_task.get_entity_judgements()
    
    if entities_to_evaluate is None:
        print "No ambiguous entities + candidates in cache. Run all_datasets_build "+\
        "script and choose to first fetch and store more entities from short texts."
        return {}
    
    for ne_obj in entities_to_evaluate:
        entity_id = ne_obj.get_entity_id()
        if entity_id not in entity_judgments:
            continue # haven't had turkers judge this entity yet
        
        # candidates that mechanical turkers selected as correct for this entity
        gold_standard_candidates = entity_judgments[entity_id]
        
        surface_form = ne_obj.surface_form
        username = ne_obj.username # authoring user
        candidate_res_objs = ne_obj.candidate_res_objs # entity's CandidateResources
        
        reslve1 = Article_ContentBOW_VSM().rank_candidates(candidate_res_objs, username)
        #reslve2 = Article_ID_VSM().rank_candidates(candidate_res_objs, username)
        #reslve3 = Article_TitleBOW_VSM().rank_candidates(candidate_res_objs, username)

        #reslve4 = DirectCategory_ID_VSM().rank_candidates(candidate_res_objs, username)
        #reslve5 = DirectCategory_TitleBOW_VSM().rank_candidates(candidate_res_objs, username)
    
        #reslve6 = CategoryGraph_ID_VSM().rank_candidates(candidate_res_objs, username)
        #reslve7 = CategoryGraph_TitleBOW_VSM().rank_candidates(candidate_res_objs, username)

        #reslve8 = Article_ContentBOW_WSD().rank_candidates_for_entity(surface_form, username, candidate_res_objs)

run_all_algorithms()