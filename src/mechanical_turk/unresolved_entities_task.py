from dataset_generation import entity_dataset_mgr, csv_util, prompt_and_print
from nltk.compat import defaultdict
from short_text_sources import short_text_websites
from wikipedia import wikipedia_api_util
import random

__entities_to_judge_csv_path__ = '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/entities-for-turk_Twitter2.csv'
__entities_results_csv_path__ = '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/mturk_entity_disambiguation_results_complete.csv'

def make_tweet_entities_csv_for_turk():
    twitter_site = short_text_websites.get_twitter_site()
    entities_to_evaluate = entity_dataset_mgr.get_valid_ne_candidates(twitter_site)
    if entities_to_evaluate is None:
        print "No ambiguous entities + candidates in cache. Run run_all_dataset_generators "+\
        "script and choose to first fetch and store more entities from short texts."
        return
    
    judged_row_plus_headers = csv_util.query_csv_for_rows(__entities_results_csv_path__, False)
    judged_row_num = 0
    already_judged = [] # list of (entity id, candidate link)
    for judge_row in judged_row_plus_headers:
        try:
            if judged_row_num==0: # row 0 is header
                entity_id_col = judge_row.index('Input.entity_id')
                candidate_link_col = judge_row.index('Input.candidate_link') 
            else:
                judged_tuple = (judge_row[entity_id_col], judge_row[candidate_link_col])
                if not judged_tuple in already_judged:
                    already_judged.append(judged_tuple)
            judged_row_num = judged_row_num+1    
        except:
            continue # just ignore a problematic row      
        
    # Determine what entity+candidate tasks we actually want to write to a spreadsheet 
    # and send to mturk since we don't have resources for unlimited mturk tasks
    tasks = {} # NamedEntity object -> candidate judgment tasks we actually want performed
    user_entities = defaultdict(list) # username -> [NamedEntity obj]
    done_shorttexts = [] # list of shorttext id
    random.shuffle(entities_to_evaluate) # so we get a random subset of a user's entities
    for ne_obj in entities_to_evaluate:
        
        # "40 nouns usually enough to establish statistically significant 
        # differences between WSD algorithms" (Santamaria et al., 2010)
        username = ne_obj.username
        if len(user_entities[username]) > 50:
            continue # have enough entities for this user
        
        # limiting our dataset to one named entity per short text
        shorttext_id = ne_obj.shorttext_id
        if shorttext_id in done_shorttexts:
            continue
        
        # no need to create tasks for candidates we already have annotator judgments for
        entity_id = ne_obj.get_entity_id()
        candidate_URLs = ne_obj.get_candidate_wikiURLs()
        valid_candidate_tasks = []
        for candidate_URL in candidate_URLs:
            if ((entity_id, candidate_URL) in already_judged):
                continue
            valid_candidate_tasks.append(candidate_URL)
        if len(valid_candidate_tasks)==0:
            continue # already have annotator judgments for all of this entity's candidates
        if len(candidate_URLs)+len(valid_candidate_tasks) < 2:
            # this would be a non-ambiguous entity, and we should never reach this 
            # point because such entities should have been filtered out by now
            raise
        tasks[entity_id] = valid_candidate_tasks
        user_entities[username].append(ne_obj)
        done_shorttexts.append(shorttext_id)
            
    # put valid entities + candidates in the spreadsheet until reach our limit of tasks
    task_max = 1400    
    
    rows = []
    headers = ['entity_id', 'short_text', 'ambiguous_entity', 'candidate_link']
    rows.append(headers)
    
    for username in user_entities:
        
        # add users until reach our limit on the number of tasks we can afford, 
        # but break at this point in the loop rather than in the inner loop to
        # ensure that we do have at least 50 entities per user (even if this
        # means we go over our task limit a little in order to reach that amount)
        if len(rows) > task_max:
            break
        
        # bypass users who haven't written the minimum number of valid entities
        # required to establish statistical significance between the algorithms
        if len(user_entities[username]) < 50:
            continue
        
        # should be 50 NamedEntity objects per user, and we'll make tasks for their candidates
        for ne_obj in user_entities[username]:
            entity_id = ne_obj.get_entity_id()
        
            # make sure the entity presented to a Turker looks the same as
            # it appears in the short text (ie with the same capitalization)
            original_shorttext = ne_obj.shorttext_str.decode('latin-1')
            surface_form = ne_obj.surface_form
            if not surface_form in original_shorttext:
                surface_form = __match_appearance__(surface_form, original_shorttext)
            
            # shuffle candidates so that they don't appear
            # in wikiminer's/dbpedia's ranking order and bias the turker
            candidate_URLs = tasks[entity_id]
            random.shuffle(candidate_URLs)
            choices = candidate_URLs[:] # copy (list slicing)
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

def analyze_entity_judgments(site):
    ''' Returns a mapping { entity ID -> { candidate link -> 
    (num turkers judged candidate relevant, num turkers judged it irrelevant) }} '''
    judgments = {} 
    
    # a mapping of turker id -> {candidate title -> true/false judgment} 
    # for each candidate annotated by the turker
    annotator_decisions = defaultdict(list)
    
    row_num = 0
    rows_plus_headers = csv_util.query_csv_for_rows(__entities_results_csv_path__, False)
    for row in rows_plus_headers:
        try:
            if row_num==0: # row 0 is header
                entity_id_col = row.index('Input.entity_id')
                candidate_link_col = row.index('Input.candidate_link') 
                
                turkerID_col = row.index('WorkerId')
                answer_col = row.index('Answer.Q1')
            else:
                judged_entity_id = row[entity_id_col]
                
                if judged_entity_id in judgments:
                    selected_candidates = judgments[judged_entity_id]
                else:
                    selected_candidates = {}
                    
                selected_candidate_title = wikipedia_api_util.get_page_title_from_url(row[candidate_link_col])
                if selected_candidate_title in selected_candidates:
                    (num_true, num_false) = selected_candidates[selected_candidate_title]
                else:
                    (num_true, num_false) = (0,0)
                    
                judgment = row[answer_col]
                if judgment=='true':
                    num_true = num_true+1
                else:
                    num_false = num_false+1
                selected_candidates[selected_candidate_title] = (num_true, num_false)
                judgments[judged_entity_id] = selected_candidates
                
                turkerID = row[turkerID_col]
                annotator_decisions[turkerID].append({selected_candidate_title:judgment})
                    
            row_num = row_num+1    
        except:
            continue # just ignore a problematic row   
        
    # Cache each annotator's decisions for later inter-rater agreement calculations
    entity_dataset_mgr.save_annotator_decisions(annotator_decisions, site)   
        
    print "Cached a total of "+str(len(judgments))+" entities judged by human Mechanical Turk annotators"
    entity_dataset_mgr.save_entity_judgements(judgments, site)
    return judgments


prompt_make_or_extract = raw_input("Make entities task for Turkers (A) or analyze completed task (B)? ")
if 'A'==prompt_make_or_extract or 'a'==prompt_make_or_extract:
    make_tweet_entities_csv_for_turk()
elif 'B'==prompt_make_or_extract or 'b'==prompt_make_or_extract:
    site = prompt_and_print.prompt_for_site()
    analyze_entity_judgments(site)
else:
    print "Unrecognized input, exiting."   
