from dataset_generation import crosssite_username_dataset_mgr, csv_util
from short_text_sources import short_text_websites

__usernames_to_judge_csv_path__ = 'usernames-for-turk.csv'
__usernames_results_csv_path__ = 'Batch_918246_batch_results.csv'

__JUDGMENT_THRESHOLD__ = 0.6

# usernames we evaluated ourselves and have confirmed 
# belong to the same individual on wikipedia and twitter
__MANUAL_OVERRIDES_TRUE__ = ['rschen7754', 'bondegezou', 'snowded', 'flameeyes', 'lquilter', 'timtrent', 'hasteur', 'esowteric', 'michaelwuzthere', '1veertje', 'elizium23', 'euchrid', 'theopolisme', 'gavbadger', 'mlpearc', 'jpbowen']
majority_unknown = ['raynevandunem', 'stuartyeates', 'slightsmile', 'Myownworst', 'eeekster', 'merlinme', 'wardmuylaert']

def make_usernames_csv_for_turk():
    print "Creating csv file of usernames for evaluation on Mechanical Turk..."
    twitter_site = short_text_websites.get_twitter_site()
    usernames_to_evaluate = crosssite_username_dataset_mgr.get_usernames_to_evaluate_mturk(twitter_site)
    print str(len(usernames_to_evaluate))+" unconfirmed usernames available:"
    print usernames_to_evaluate
    
    # dump to csv
    username_rows = [[username] for username in usernames_to_evaluate]
    csv_util.write_to_spreadsheet(__usernames_to_judge_csv_path__, username_rows, None)
        
def update_usernames_csv_with_judgments():
    ''' Handles updating the cross-site-usernames 
    spreadsheet given new Mechanical Turker evaluations '''
    print "Updating cross-site-usernames spreadsheet with Mechanical Turker "+\
    "judgments about username matching from spreadsheet of results..."
    
    twitter_site = short_text_websites.get_twitter_site()
    evaluated_usernames = crosssite_username_dataset_mgr.get_usernames_to_evaluate_mturk(twitter_site)
    
    judgments = {}
    row_num = 0
    rows_plus_headers = csv_util.query_csv_for_rows(__usernames_results_csv_path__, False)
    for row in rows_plus_headers:
        try:
            if row_num==0: # row 0 is header
                username_col = row.index('Input.user')
                turkerID_col = row.index('WorkerId')
                answer_col = row.index('Answer.Q1')
            else:
                judged_username = row[username_col]
                if not judged_username in evaluated_usernames:
                    raise # this shouldn't happen so see what's going on..
                
                if judged_username in judgments:
                    evaluations = judgments[judged_username]
                else:
                    evaluations = Turker_Username_Evaluation(judged_username)
                    judgments[judged_username] = evaluations
                    
                workerID = row[turkerID_col]
                judgment = row[answer_col]
                if 'True'==judgment:
                    evaluations.add_true_eval(workerID)
                elif 'False'==judgment:
                    evaluations.add_false_eval(workerID)
                else:
                    evaluations.add_unknown_eval(workerID)
                
            row_num = row_num+1    
        except:
            continue # just ignore a problematic assignment row
        
    # Get the usernames that all workers agreed belonged to a single 
    # person (ie ignore usernames that were rejected by any worker)
    unanimous_confirmed_usernames = []
    likely_usernames = []
    conflicting_judgments = []
    for username in judgments:
        
        if username in __MANUAL_OVERRIDES_TRUE__:
            likely_usernames.append(username)
            continue
        
        evaluation = judgments[username]
        eval_score = evaluation.get_eval_measure()
        print "Match score for "+str(username)+": "+str(eval_score)
        
        if eval_score>=__JUDGMENT_THRESHOLD__:
            likely_usernames.append(username)
        elif evaluation.get_number_true_evals()>0:
            conflicting_judgments.append(username)
        
        # Each username given to 5 turkers to evaluate. 
        if (evaluation.get_number_true_evals()>0 and 
            evaluation.get_number_false_evals()==0 and 
            evaluation.get_number_unknown_evals()==0):
            # all turkers unanimously confirmed this username
            unanimous_confirmed_usernames.append(username)
    print "Judged "+str(len(judgments))+" usernames"
    print "Likely matches"+str(len(likely_usernames))
    print "Conflicting judgments:"+str(conflicting_judgments) 
            
    # Update the judgment cell in the spreadsheet for unanimously confirmed usernames 
    crosssite_username_dataset_mgr.update_confirmed_usernames(twitter_site,
                                                              likely_usernames)
    print "Updated cross-site-usernames spreadsheet to reflect unanimous positive confirmations"
    
        
class Turker_Username_Evaluation:
    ''' Represents a set of judgments by Mechanical Turk workers about 
     whether or not a username corresponds to the same individual person. '''
    
    def __init__(self, username):
        self.username = username
        self.true_evals = [] # workers who confirmed username as same individual
        self.false_evals = [] # workers who rejected username as same individual
        self.unknown_evals = [] # workers who were unable to confirm or reject
        
    def add_true_eval(self, workerID):
        self.true_evals.append(workerID)
    def add_false_eval(self, workerID):
        self.false_evals.append(workerID)
    def add_unknown_eval(self, workerID):
        self.unknown_evals.append(workerID)
        
    def get_number_true_evals(self):
        ''' Returns the number of unique workers that judged the 
        given username to belong to a single individual '''
        return len(set(self.true_evals))
    def get_number_false_evals(self):
        return len(set(self.false_evals))
    def get_number_unknown_evals(self):
        return len(set(self.unknown_evals))
        
    def get_eval_measure(self):
        ''' Returns an averaged measure of the likelihood this username belongs to a single
        individual, where True, False, and Unknown judgments contribute the following: 
        a judgment of True = 1
        a judgment of False = 0
        a judgment of Unknown = 0.5
        '''
        num_true = self.get_number_true_evals()
        num_false = self.get_number_false_evals()
        num_unknown = self.get_number_unknown_evals()
        print str(self.username)+" (true, false, unknown) judgments: "+str(num_true)+", "+str(num_false)+", "+str(num_unknown)
        
        #no_unknowns = ((num_true*1.0) + (num_false*0.0)) / (num_true + num_false)        
        
        sum_evals = (num_true*1.0) + (num_false*0.0) + (num_unknown*0.5)
        avg_evals = sum_evals / (num_true + num_false + num_unknown)
        return avg_evals
        
prompt_make_or_extract = raw_input("Make username task for Turkers (A) or analyze completed task (B)? ")
if 'A'==prompt_make_or_extract or 'a'==prompt_make_or_extract:
    make_usernames_csv_for_turk()
elif 'B'==prompt_make_or_extract or 'b'==prompt_make_or_extract:
    update_usernames_csv_with_judgments()
else:
    print "Unrecognized input, exiting."
