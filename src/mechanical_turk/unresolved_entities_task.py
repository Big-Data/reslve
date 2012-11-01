from dataset_generation import entity_dataset_mgr, csv_util, pkl_util
from short_text_sources import short_text_websites
import random

__entities_to_judge_csv_path__ = '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/entities-for-turk.csv'

__entities_results_csv_path__ = '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/mturk_entity_disambiguation_results_complete.csv'
__entity_judgments_cache_path__ = '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/entity_judgments_cache.pkl'

def make_tweet_entities_csv_for_turk():
    twitter_site = short_text_websites.get_twitter_site()
    entities_to_evaluate = entity_dataset_mgr.get_valid_ne_candidates(twitter_site)
    if entities_to_evaluate is None:
        print "No ambiguous entities + candidates in cache. Run run_all_dataset_generators "+\
        "script and choose to first fetch and store more entities from short texts."
        return
    
    rows = []
    headers = ['entity_id', 'short_text', 'ambiguous_entity', 'candidate_link']
    rows.append(headers)
    
    # put valid entities + candidates in the spreadsheet
    progress = 0
    for ne_obj in entities_to_evaluate:
        
        progress = progress+1
        if progress%50==0:
            print str(progress)+" out of "+str(len(entities_to_evaluate))
        '''    keep_adding = raw_input("Added "+str(len(rows)-1)+" to spreadsheet out of "+str(len(entities_to_evaluate))+". Continue adding more? (Y/N)")
            if 'Y'!=keep_adding and 'y'!=keep_adding:
                break
        '''
            
        # shuffle candidates so that they don't appear
        # in wikiminer's ranking order and bias the turker
        candidate_URIs = ne_obj.get_candidate_URIs()
        if len(candidate_URIs)<=1:
            continue # have to have at least 2 candidates to be ambiguous
        random.shuffle(candidate_URIs)
        choices = candidate_URIs[:] # copy (list slicing)
            
        # make sure the entity presented to a Turker looks the same as
        # it appears in the short text (ie with the same capitalization)
        original_shorttext = ne_obj.shorttext_str.decode('latin-1')
        surface_form = ne_obj.surface_form
        if not surface_form in original_shorttext:
            surface_form = __match_appearance__(surface_form, original_shorttext)
        
        '''
        # Tell turker to read the short text
        print "\nRead the following piece of text: \""+str(dirty_shorttext)+"\""
        
        # Tell turker to look at entity and choose correct candidate
        print "From the below set of choices, please select the Wikipedia page "+\
        "that corresponds to the correct meaning of the word or phrase, \""\
        +str(entity_str)+"\""
        print "Choices: "+str(choices)
        '''
        
        entity_id = ne_obj.get_entity_id()
        for choice in choices:
            # make a separate row for each candidate link 
            # rather than putting all links in a single cell
            row = [entity_id, original_shorttext, surface_form, choice]
            rows.append(row)
        
        if len(rows)%50==0:
            # write the rows every once in a while in case we reach an error
            print "Updating spreadsheet..."+str(len(rows))
            csv_util.write_to_spreadsheet(__entities_to_judge_csv_path__, rows)
        
    # dump to csv
    csv_util.write_to_spreadsheet(__entities_to_judge_csv_path__, rows)
    
def __match_appearance__(surface_form, shorttext_str):
    ''' Seems that Wikipedia Miner sometimes returns an entity 
    capitalized even if it is lowercase in the original string '''
    if surface_form.lower() in shorttext_str:
        return surface_form.lower()
    return surface_form

def get_entity_judgements():
    output_str = "Candidate entities judged by Mechanical Turkers..."
    entity_judgments = pkl_util.load_pickle(output_str, 
                                            __entity_judgments_cache_path__)
    if entity_judgments is None:
        entity_judgments = analyze_entities_judgments(output_str)
    return entity_judgments

def analyze_entities_judgments(output_str):
    ''' Handles updating the entities 
    spreadsheet given new Mechanical Turker evaluations '''
    print "Updating entities spreadsheet with Mechanical Turker "+\
    "judgments about correct candidate resources..."
    
    judgments = {} # maps { entity ID -> { candidate link -> (num times judged correct, num times judged wrong) }}
    row_num = 0
    rows_plus_headers = csv_util.query_csv_for_rows(__entities_results_csv_path__, False)
    for row in rows_plus_headers:
        try:
            if row_num==0: # row 0 is header
                entity_id_col = row.index('Input.entity_id')
                candidate_link_col = row.index('Input.candidate_link') 
                
                #turkerID_col = row.index('WorkerId')
                answer_col = row.index('Answer.Q1')
            else:
                judged_entity_id = row[entity_id_col]
                
                if judged_entity_id in judgments:
                    selected_candidates = judgments[judged_entity_id]
                else:
                    selected_candidates = {}
                    
                selected_candidate = row[candidate_link_col]
                if selected_candidate in selected_candidates:
                    (num_true, num_false) = selected_candidates[selected_candidate]
                else:
                    (num_true, num_false) = (0,0)
                    
                judgment = row[answer_col]
                if judgment=='true':
                    num_true = num_true+1
                else:
                    num_false = num_false+1
                selected_candidates[selected_candidate] = (num_true, num_false)
                judgments[judged_entity_id] = selected_candidates
                    
            row_num = row_num+1    
        except:
            continue # just ignore a problematic row    
        
    # Get the candidates that workers agreed upon for each entity.
    # For now, ignoring entities that all workers could not select the same candidate for
    turker_selected_candidates = {}
    for entity_id in judgments:
        agreed_candidates = []
        candidate_judgments = judgments[entity_id]
        for candidate_link in candidate_judgments:
            (num_true, num_false) = candidate_judgments[candidate_link]
            if num_true > num_false:
                # TODO need to figure out threshold for agreement. require 
                # turkers to unanimously select a candidate as correct?
                agreed_candidates.append(candidate_link)
        turker_selected_candidates[entity_id] = agreed_candidates
    
    print "Cached a total of "+str(len(turker_selected_candidates))+" Turker judgements about ambiguous entities"
    pkl_util.write_pickle(output_str, turker_selected_candidates, __entity_judgments_cache_path__)
    
    return turker_selected_candidates


prompt_make_or_extract = raw_input("Make entities task for Turkers (A) or analyze completed task (B)? ")
if 'A'==prompt_make_or_extract or 'a'==prompt_make_or_extract:
    make_tweet_entities_csv_for_turk()
elif 'B'==prompt_make_or_extract or 'b'==prompt_make_or_extract:
    get_entity_judgements()
else:
    print "Unrecognized input, exiting."   
