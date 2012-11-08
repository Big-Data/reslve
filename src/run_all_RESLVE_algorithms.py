from dataset_generation import prompt_and_print
from ranking_algorithms.article_VSM import Article_ContentBOW_VSM, \
    Article_ID_VSM, Article_TitleBOW_VSM
from ranking_algorithms.article_WSD import Article_ContentBOW_WSD
from ranking_algorithms.direct_categories import DirectCategory_ID_VSM, \
    DirectCategory_TitleBOW_VSM
from ranking_algorithms.graph_categories import CategoryGraph_ID_VSM, \
    CategoryGraph_TitleBOW_VSM
from results import performance
import RESLVE_rankings_mgr

def run_RESLVE():
    # Prompt to ask from which site we want to disambiguate entities
    try:
        site = prompt_and_print.prompt_for_site()
    except KeyError:
        print "Sorry, that is not a recognized site. Exiting."
        return
    
    reslve_algorithms = __get_RESLVE_algorithm_constructors__()
    
    alg_num = raw_input("Which RESLVE algorithm do you want to run? "+\
    "\n1=Article Content, 2=Article ID, 3=Article Title, 4=Direct Category ID, "+\
    "5=Direct Category Title, 6=Category Graph ID, 7=Category Graph Title, 8 = Article Content WSD")
    cache_resolved_entities = raw_input("Cache resolved entities? (Y/N): ")
    
    RESLVE_alg = reslve_algorithms[alg_num]()
    resolved_entities = RESLVE_rankings_mgr.run_all_algorithms(RESLVE_alg, site, cache_resolved_entities)

    # evaluate and compare performance
    performance.compare_ranking_precision(resolved_entities)
    performance.eval_annotator_agreement(site)
    

def __get_RESLVE_algorithm_constructors__():
    ''' The constructors of the various RESLVE algorithms
    that can be used to create a reslve_algorithm object '''
    
    # RESLVE algorithms based on articles' page content
    article_contentBowVsm = Article_ContentBOW_VSM
    article_idVsm = Article_ID_VSM
    article_titleBowVsm = Article_TitleBOW_VSM
    
    # RESLVE algorithms based on articles' direct categories
    directCategory_idVsm = DirectCategory_ID_VSM
    directCategory_titleBowVsm = DirectCategory_TitleBOW_VSM
    
    # RESLVE algorithms based on articles' full category hierarchy
    graphCategory_idVsm = CategoryGraph_ID_VSM
    graphCategory_titleBowVsm = CategoryGraph_TitleBOW_VSM

    # RESLVE algorithm based on WSD lesk approach
    articleContent_bowWsd = Article_ContentBOW_WSD
    
    reslve_algorithms = [article_contentBowVsm, article_idVsm, article_titleBowVsm, 
                         directCategory_idVsm, directCategory_titleBowVsm, 
                         graphCategory_idVsm, graphCategory_titleBowVsm, 
                         articleContent_bowWsd]
    return reslve_algorithms