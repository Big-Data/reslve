''' 
Measures how much Turkers agree or disagree about whether or not a candidate
resource for an ambiguous entity is relevant or not relevant. 

Values of kappa between 2/3 and 1.0 generally considered acceptable. 
'''
from dataset_generation import entity_dataset_mgr
from nltk.metrics.agreement import AnnotationTask
from segeval.agreement import Kappa, Pi, Bias
import random
import segeval.agreement

def compute_annotator_agreement(site):
    ''' Computes both percentage of agreement among raters, Pr(a), 
    as well as Kappa Coefficient to correct for chance agreement. '''
    
    kappa_total = 0
    n = 0
    annotator_decisions = entity_dataset_mgr.get_annotator_decisions(site)
    for worker_id1 in annotator_decisions:
        for worker_id2 in annotator_decisions:
            if worker_id1==worker_id2:
                continue

            rater1_labels = annotator_decisions[worker_id1]
            rater1_tasks = [task_eval_dict.keys()[0] for task_eval_dict in rater1_labels]
        
            rater2_labels = annotator_decisions[worker_id2]
            rater2_tasks = [task_eval_dict.keys()[0] for task_eval_dict in rater2_labels]
        
            common_tasks = set(rater1_tasks).intersection(set(rater2_tasks))
            if len(common_tasks)==0:
                continue # these two turkers didn't evaluate any of the same candidates 
        
            # determine the agreements/disagreements for a contingency table
            (A_cell, B_cell, C_cell, D_cell) = build_contingency_table(common_tasks, 
                                                                       rater1_labels, rater2_labels)
                
            # compute relative observed agreement among raters Pr(a)
            Pra = (A_cell + D_cell) / float(A_cell + B_cell + C_cell + D_cell)
            #print "Pr(a) = "+str(Pra)
            
            # compute kappa coefficient of inter-rater agreement
            kappa = calculate_kappa(Pra, A_cell, B_cell, C_cell, D_cell)
    
            kappa_total = kappa_total+kappa
            n = n+1
    avg_kappa = kappa_total/n
    print "Average kappa = "+str(avg_kappa)
    
def build_contingency_table(common_tasks, rater1_labels, rater2_labels):
    '''
    Builds the contingency table:
                 w1      w2
                true   false
    w1  true     A       B
    w2  false    C       D
    '''
    A_cell = 0 # both workers annotated candidate as relevant
    B_cell = 0 # worker1 annotated candidate as relevant, worker2 as not relevant
    C_cell = 0 # worker1 annotated candidate as not relevant, worker2 as relevant
    D_cell = 0 # both workers annotated candidate as not relevant
    
    for common_task in common_tasks:

        # get the judgment each turker made for this candidate they both evaluated
        rater1_label = __get_rater_label__(common_task, rater1_labels)
        rater2_label = __get_rater_label__(common_task, rater2_labels)
        if rater1_label==None or rater2_label==None:
            raise # this should never happen because
        
        if rater1_label=='true' and rater2_label=='true':
            A_cell = A_cell+1
        if rater1_label=='true' and rater2_label=='false':
            B_cell = B_cell+1
        if rater1_label=='false' and rater2_label=='true':
            C_cell = C_cell+1
        if rater1_label=='false' and rater2_label=='false':
            D_cell = D_cell+1   
             
    return (A_cell, B_cell, C_cell, D_cell)

def calculate_prob_chance_agreement(A_cell, B_cell, C_cell, D_cell):
    ''' Computes probability of random agreement, Pr(e) '''
    
    table_sum = float(A_cell + B_cell + C_cell + D_cell)
    
    # probability both would randomly label a candidate as relevant
    w1_rel = float(A_cell + B_cell) / table_sum
    w2_rel = float(A_cell + C_cell) / table_sum
    both_rel_random = float(w1_rel*w2_rel) 

    # probability both would randomly label a candidate as relevant
    # (same as 1-w1_rel=C_cell+D_cell and 1-w2_rel=B_cell+D_cell)    
    w1_notrel = float(C_cell+D_cell) / table_sum
    w2_notrel = float(B_cell+D_cell) / table_sum
    both_notrel_random = float(w1_notrel*w2_notrel)
    
    Pre = float(both_rel_random)+float(both_notrel_random)
    return Pre    
    
def calculate_kappa(Pra, A_cell, B_cell, C_cell, D_cell):
    if Pra==1:
        # if raters are in complete agreement then kappa = 1
        #print "Kappa = 1"
        return 1
    Pre = calculate_prob_chance_agreement(A_cell, B_cell, C_cell, D_cell)
    kappa = float(Pra - Pre) / float(1 - Pre)
    #print "Kappa = "+str(kappa)
    return kappa

def __get_rater_label__(task, rater_labels):
    for task_dict in rater_labels:
        rater_task = task_dict.keys()[0]
        if task==rater_task:
            rater_label = task_dict[rater_task]
            return rater_label
    return None

def compute_annotator_agreement_libs(site):
    ''' Computes various annotator agreement measures using 
    NLTK's metrics.agreement and SegEval's Agreement metrics '''
    
    # NLTK's AnnotationTask expects list of triples, each containing one rater's
    # label for one candidate, ie [(rater, item, label),(rater, item, label),...]
    # See http://nltk.org/api/nltk.metrics.html#nltk.metrics.agreement
    nltk_dataArray = [] 
    
    # SegEval expects items_masses dict { item -> { coder -> [label] } } 
    # See http://packages.python.org/segeval/segeval.agreement/
    segeval_items_masses = {}

    # 3 raters for each candidate judgment
    raters = ['rater1','rater2','rater3']
    judgments = entity_dataset_mgr.get_entity_judgements(site)
    
    # iterate through the rater's labels to put them into the 
    # proper data formats that the different agreement libs require
    for entity_id in judgments:
        candidate_labels = judgments[entity_id]
        for candidate_title in  candidate_labels:
            (num_true, num_false) = candidate_labels[candidate_title]
            
            if num_true+num_false!=3:
                raise # we ask for 3 turkers per candidate eval task
            
            # check for the case when all raters choose the same label
            unanimous_decision = None
            if num_true==0:
                unanimous_decision = 'false_label'
            elif num_false==0:
                unanimous_decision = 'true_label'
            if unanimous_decision!=None:
                # all raters labeled this candidate either
                # unanimously with true or unanimously with false
                segeval_rater_map = {}
                for rater in raters:
                    
                    # data=[(rater, item, label),(rater, item, label),...]
                    nltk_dataArray.append((rater, candidate_title, unanimous_decision))
                    
                    # { coder -> [labels] } 
                    segeval_rater_map[rater] = [unanimous_decision]
                
                # add to items masses, which looks like { item -> { coder -> [label] } } 
                segeval_items_masses[str(entity_id+candidate_title)] = segeval_rater_map   
                
            else:
                # decision was split, so randomly select a number of raters
                # equal to num_true and a number of raters equal to num_false
                raters_copy = raters[:]
                random.shuffle(raters_copy)
                segeval_rater_map = {}
                for rater in raters_copy[:num_true]:
                    nltk_dataArray.append((rater, candidate_title, 'true_label')) # [(rater, item, label)...]
                    segeval_rater_map[rater] = ['true_label'] # { coder -> [labels] } 
                for rater in raters_copy[num_true:]:
                    nltk_dataArray.append((rater, candidate_title, 'false_label')) # [(rater, item, label)...]
                    segeval_rater_map[rater] = ['false_label'] # { coder -> [labels] } 
                    
    compute_annotator_agreement_nltkmetrics(nltk_dataArray)
    compute_annotator_agreement_segeval(segeval_items_masses)
                    
def compute_annotator_agreement_nltkmetrics(data_array):
    ''' See http://nltk.org/api/nltk.metrics.html#nltk.metrics.agreement '''
    
    print "####### Agreement coefficients according to NLTK metrics.agreement #######"
    
    t = AnnotationTask(data=data_array)
    print "Average observed agreement across all coders and items:"+str(t.avg_Ao())
    
    print "Cohen's Kappa (Cohen 1960): "+str(t.kappa())
    print "Weighted kappa (Cohen 1968): "+str(t.weighted_kappa())
    
    print "Scott's pi (Scott 1955): "+str(t.pi())
    #print "pi_avg: "+str(t.pi_avg())
    
    print "alpha (Krippendorff 1980): "+str(t.alpha())
    
    print "Observed disagreement for the alpha coefficient: "+str(t.Do_alpha())
    print "S (Bennett, Albert and Goldstein 1954): "+str(t.S())
    #print "n-notation used in Artstein and Poesio (2007): "+str(t.N(k=, ic???))
    print "Observed disagreement for the weighted kappa coefficient averaged over all labelers: "+str(t.Do_Kw())
    
def compute_annotator_agreement_segeval(items_masses):
    ''' See http://packages.python.org/segeval/segeval.agreement/ '''
    
    print "####### Agreement according to SegEval #######"
    
    print "Actual (ie, observed or Aa), segmentation agreement without accounting for chance: "+str(segeval.agreement.actual_agreement(items_masses))
    
    print "Cohen's Kappa (Cohen 1960)"+str(Kappa.cohen_kappa(items_masses))
    print "Fleiss' Kappa (or multi-Kappa) (Davies Fleiss 1982): "+str(Kappa.fleiss_kappa(items_masses))
    
    print "Scott's pi (Scott 1955): "+str(Pi.scotts_pi(items_masses))
    print "Fleiss' Pi (or multi-Pi) originally proposed (Fleiss 1971): "+str(Pi.fleiss_pi(items_masses))
   
    print "Artstein and Poesio's annotator bias, or B (Artstein Poesio 2008): "+str(Bias.artstein_poesio_bias(items_masses))
    