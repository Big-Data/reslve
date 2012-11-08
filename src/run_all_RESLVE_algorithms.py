from CONSTANT_VARIABLES import get_RESLVE_algorithm_constructors
from dataset_generation import prompt_and_print
from results import performance
import RESLVE_rankings_mgr

def run_RESLVE():
    # Prompt to ask from which site we want to disambiguate entities
    try:
        site = prompt_and_print.prompt_for_site()
    except KeyError:
        print "Sorry, that is not a recognized site. Exiting."
        return
    
    reslve_algorithms = get_RESLVE_algorithm_constructors()
    
    alg_num = raw_input("Which RESLVE algorithm do you want to run? "+\
    "\n1=Article Content, 2=Article ID, 3=Article Title, 4=Direct Category ID, "+\
    "5=Direct Category Title, 6=Category Graph ID, 7=Category Graph Title, 8 = Article Content WSD")
    cache_resolved_entities = raw_input("Cache resolved entities? (Y/N): ")
    
    RESLVE_alg = reslve_algorithms[alg_num]()
    resolved_entities = RESLVE_rankings_mgr.run_all_algorithms(RESLVE_alg, site, cache_resolved_entities)

    # evaluate and compare performance
    performance.compare_ranking_precision(resolved_entities)
    performance.eval_annotator_agreement(site)