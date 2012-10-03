from dataset_generation import crosssite_username_dataset_mgr, csv_util
from short_text_sources import short_text_websites

__usernames_to_judge_csv_path__ = 'usernames-for-turk.csv'
__usernames_results_csv_path__ = 'Batch_918246_batch_results.csv'

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
    for username in judgments:
        evaluation = judgments[username]
        num_confirmations = evaluation.get_number_true_evals()
        # Each username given to 5 workers to evaluate. 
        # For now, only consider usernames that all workers unanimously agree on
        if num_confirmations==5:
            unanimous_confirmed_usernames.append(username)
            
    # Update the judgment cell in the spreadsheet for unanimously confirmed usernames 
    crosssite_username_dataset_mgr.update_confirmed_usernames(twitter_site, 
                                                              unanimous_confirmed_usernames)
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
        
        
prompt_make_or_extract = raw_input("Make username task for Turkers (A) or analyze completed task (B)? ")
if 'A'==prompt_make_or_extract or 'a'==prompt_make_or_extract:
    make_usernames_csv_for_turk()
elif 'B'==prompt_make_or_extract or 'b'==prompt_make_or_extract:
    update_usernames_csv_with_judgments()
else:
    print "Unrecognized input, exiting."
