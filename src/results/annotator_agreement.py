''' 
Measures how much Turkers agree or disagree about whether or not a candidate
resource for an ambiguous entity is relevant or not relevant. 

Computes both percentage of agreement among raters, Pr(a), as well as Kappa 
Coefficient to correct for chance agreement.

Values of kappa between 2/3 and 1.0 generally considered acceptable. 
'''

def compute_annotator_agreement(annotator_decisions):
    
    kappa_total = 0
    n = 0
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
            print "Pr(a) = "+str(Pra)
            
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
        print "Kappa = 1"
        return 1
    Pre = calculate_prob_chance_agreement(A_cell, B_cell, C_cell, D_cell)
    kappa = float(Pra - Pre) / float(1 - Pre)
    print "Kappa = "+str(kappa)
    return kappa

def __get_rater_label__(task, rater_labels):
    for task_dict in rater_labels:
        rater_task = task_dict.keys()[0]
        if task==rater_task:
            rater_label = task_dict[rater_task]
            return rater_label
    return None
