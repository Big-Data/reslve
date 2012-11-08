from nltk.compat import defaultdict
from results import annotator_agreement

def compare_ranking_precision(resolved_entities):

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
    
    toolkit_failures = 0
    reslve_success_when_toolkits_fail = 0

    for resolved_entity in resolved_entities:
        gold_standard_candidates = resolved_entity.get_unanimous_candidates_goldstandard()
        if len(gold_standard_candidates)==0:
            annotator_disagreement = annotator_disagreement+1
            continue # turkers couldn't agree on this entity
        
        is_wikiminer_correct = resolved_entity.is_baseline_wikiminer_correct()
        is_dbpedia_correct = resolved_entity.is_baseline_dbpedia_correct()
        
        for alg_id in resolved_entity.reslve_rankings.keys():
            
            # check if RESLVE algorithm selected the correct candidate
            is_reslve_algs_correct = resolved_entity.is_reslve_correct(alg_id)
            if is_reslve_algs_correct:
                reslve_algs_correct[alg_id] = reslve_algs_correct[alg_id]+1
                
            # run the same RESLVE algorithm but use a random non-matching user who
            # doesn't provide the user interest model we claim is so relevant and
            # valuable (ie we want to make sure that just incorporating any random 
            # wikipedia data isn't the main reason for any good performance we see) 
            if resolved_entity.is_baseline_reslve_nonmatch_correct(alg_id):
                nonmatch_algs_baseline_correct[alg_id] = nonmatch_algs_baseline_correct[alg_id]+1
        
            # measure whether when toolkits are wrong, RESLVE can perform correctly
            if not is_wikiminer_correct and not is_dbpedia_correct:
                toolkit_failures = toolkit_failures+1
                if is_reslve_algs_correct:
                    reslve_success_when_toolkits_fail = reslve_success_when_toolkits_fail+1                
            
        # check performance of the base line strategies
        if is_wikiminer_correct:
            wikiminer_correct = wikiminer_correct+1
        if is_dbpedia_correct:
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
        if nonmatch_baseline_correct==0:
            improvement_str =  "Infinite (non match baseline failed to correctly resolve any entity)"
        else:
            matching_user_improvement = float(reslve_correct-nonmatch_baseline_correct)/float(nonmatch_baseline_correct)
            improvement_str = str(matching_user_improvement)
        print "Improvement boost by incorporating user interest model into RESLVE's "+\
        str(alg_id)+": "+str(improvement_str)
        
    if toolkit_failures==0:
        print "Toolkits performed with 100% accuracy.."    
    else:
        tough_cases_improvement = float(reslve_success_when_toolkits_fail)/float(toolkit_failures)
        print "RESLVE able to achieve "+str(tough_cases_improvement)+\
        " precision in the difficult cases when Wikipedia Miner and DBPedia Spotlight fail completely."
        
def eval_annotator_agreement(site):
    # our own implementation of some standard agreement metrics
    annotator_agreement.compute_annotator_agreement(site) 
    
    # additional agreement measures using nltk and segeval
    annotator_agreement.compute_annotator_agreement_libs(site) 
