from dataset_generation import prompt_and_print
from nltk.compat import defaultdict
import RESLVE_rankings_mgr
    

def compare_ranking_precision(site):
    
    # load cache of ResolvedEntity objects
    resolved_entities = RESLVE_rankings_mgr.get_resolved_entities(site, False)
    
    # the total number of entities we have unanimous annotator judgments for
    total_evaluated = 0
    
    # the total number of entities for which turkers
    # could not agree upon the correct candidate
    annotator_disagreement = 0
    gold_correct = 0
    
    # the total number of entities for which our algorithms and the 
    # baseline ranking techniques selected the correct candidate
    reslve_algs_correct = defaultdict(int) # alg id -> # times correct
    nonmatch_algs_baseline_correct = defaultdict(int)
    wikiminer_correct = 0
    dbpedia_correct = 0
    random_correct = 0
    
    for resolved_entity in resolved_entities:
        
        gold_standard_candidates = resolved_entity.get_unanimous_candidates_goldstandard()
        if len(gold_standard_candidates)==0:
            annotator_disagreement = annotator_disagreement+1
            continue # turkers couldn't agree on this entity
        
        for alg_id in resolved_entity.reslve_rankings.keys():
            if resolved_entity.is_reslve_correct(alg_id):
                reslve_algs_correct[alg_id] = reslve_algs_correct[alg_id]+1
            if resolved_entity.is_baseline_reslve_nonmatch_correct(alg_id):
                nonmatch_algs_baseline_correct[alg_id] = nonmatch_algs_baseline_correct[alg_id]+1
        if resolved_entity.is_baseline_wikiminer_correct():
            wikiminer_correct = wikiminer_correct+1
        if resolved_entity.is_baseline_dbpedia_correct():
            dbpedia_correct = dbpedia_correct+1
        if resolved_entity.is_baseline_random_correct():
            random_correct = random_correct+1
        if resolved_entity.is_goldstandard_correct():
            gold_correct = gold_correct+1  
        
        total_evaluated = total_evaluated+1     
    
    wikiminer_accuracy = float(wikiminer_correct)/float(total_evaluated)
    print "Wikipedia Miner precision: "+str(wikiminer_accuracy)
    
    dbpedia_accuracy = float(dbpedia_correct)/float(total_evaluated)
    print "DBPedia Spotlight precision: "+str(dbpedia_accuracy)
    
    random_accuracy = float(random_correct)/float(total_evaluated)
    print "Random baseline precision: "+str(random_accuracy)
    
    gold_accuracy = float(gold_correct)/float(total_evaluated)
    print "Human annotator ability to reach consensus: "+str(gold_accuracy)    
    
    for alg_id in resolved_entity.reslve_rankings.keys():
        reslve_correct = reslve_algs_correct[alg_id]
        reslve_accuracy = float(reslve_correct)/float(total_evaluated)
        print "RESLVE "+alg_id+" precision: "+str(reslve_accuracy)
        
        nonmatch_baseline_correct = nonmatch_algs_baseline_correct[alg_id]
        nonmatch_baseline_accuracy = float(nonmatch_baseline_correct)/float(total_evaluated)
        print "RESLVE nonmatch baseline using "+alg_id+" precision: "+str(nonmatch_baseline_accuracy)
        
        # improvement achieved by incorporating the user interest model
        matching_user_improvement = float(reslve_correct-nonmatch_baseline_correct)/float(nonmatch_baseline_correct)
        print "Improvement boost by incorporating user interest model into RESLVE "+\
        alg_id+" improvement: "+str(matching_user_improvement)
        
    
# Prompt to ask which site's short text entities we want to disambiguate
try:
    site = prompt_and_print.prompt_for_site()
    compare_ranking_precision(site)
except KeyError:
    print "Sorry, that is not a recognized site. Exiting."
