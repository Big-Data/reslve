from dataset_generation import entity_dataset_mgr, csv_util
from short_text_sources import short_text_websites
from wikipedia import wikipedia_api_util
import random

__entities_to_judge_csv_path__ = 'entities-for-turk.csv'

def make_tweet_entities_csv_for_turk():
    twitter_site = short_text_websites.get_twitter_site()
    entities_to_evaluate = entity_dataset_mgr.get_ne_candidates_to_evaluate_mturk(twitter_site)
    if entities_to_evaluate is None:
        print "No ambiguous entities + candidates in cache. Run run_all_dataset_generators "+\
        "script and choose to first fetch and store more entities from short texts."
        return
    
    rows = []
    headers = ['entity_id', 'short_text', 'ambiguous_entity', 'candidate_link']
    rows.append(headers)
    
    # Some instructions for the task
    progress = 0
    for ne_obj in entities_to_evaluate:
        
        progress = progress+1
        if progress%50==0:
            print progress
        '''    keep_adding = raw_input("Added "+str(len(rows)-1)+" to spreadsheet out of "+str(len(entities_to_evaluate))+". Continue adding more? (Y/N)")
            if 'Y'!=keep_adding and 'y'!=keep_adding:
                break
        '''
        if not ne_obj.is_valid_entity():
            continue
        
        # shuffle candidates so that they don't appear
        # in wikiminer's ranking order and bias the turker
        candidate_res_objs = ne_obj.candidate_res_objs
        if len(candidate_res_objs)<=1:
            continue # have to have at least 2 candidates to be ambiguous
        candidate_URIs = [wikipedia_api_util.get_wikipedia_page_url(candidate_res_title)
                          for candidate_res_title in candidate_res_objs]
        random.shuffle(candidate_URIs)
        choices = candidate_URIs[:] # copy (list slicing)
            
        # make sure the entity presented to a Turker looks the same as
        # it appears in the short text (ie with the same capitalization)
        original_shorttext = ne_obj.shorttext_str
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
    
make_tweet_entities_csv_for_turk()
