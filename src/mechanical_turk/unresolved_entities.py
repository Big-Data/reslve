from dataset_generation import entity_dataset_mgr, csv_util
from short_text_sources import short_text_websites
from wikipedia import wikipedia_api_util
import random

__entities_to_judge_csv_path__ = 'entities-for-turk.csv'

def make_entities_csv_for_turk():
    twitter_site = short_text_websites.get_twitter_site()
    entities_to_evaluate = entity_dataset_mgr.get_ne_candidates_to_evaluate_mturk(twitter_site)
    if entities_to_evaluate is None:
        print "No ambiguous entities + candidates in cache. Run all_datasets_build "+\
        "script and choose to first fetch and store more entities from short texts."
        return
    
    rows = []
    headers = ['short_text', 'ambiguous_entity', 'candidates']
    rows.append(headers)
    
    # Some instructions for the task
    for surface_form_obj in entities_to_evaluate:
        
        # Tell turker to read the short text
        dirty_shorttext = surface_form_obj.shorttext_str
        print "\nRead the following piece of text: \""+str(dirty_shorttext)+"\""
        
        # Tell turker to look at entity and choose correct candidate
        entity_str = surface_form_obj.entity_str
        
        # make sure the entity presented to a Turker looks the same as
        # it appears in the short text (ie with the same capitalization)
        if not entity_str in dirty_shorttext:
            entity_str = __match_appearance__(entity_str, dirty_shorttext)
        
        print "From the below set of choices, please select the correct intended meaning of the term \""\
        +str(entity_str)+"\""
        
        print "Note: You can check the supplied Wikipedia page of a choice if it will help you better understand its meaning."
        print "Choices:"
        # shuffle candidates so that they don't appear
        # in wikiminer's ranking order and bias the turker
        choices = []
        candidates = surface_form_obj.candidates
        random.shuffle(candidates)
        for candidate in candidates:
            candidate_title = candidate['title'] 
            candidate_wikipage = wikipedia_api_util.get_wikipedia_page_url(candidate_title)
            choice = str(candidate_title)+" ("+str(candidate_wikipage)+")"
            print choice
            choices.append(choice)
            
        row = [dirty_shorttext, entity_str, choices]
        rows.append(row)
            
    # dump to csv
    csv_util.write_to_spreadsheet(__entities_to_judge_csv_path__, rows)
    
def __match_appearance__(entity_str, shorttext_str):
    ''' Seems that Wikipedia Miner sometimes returns an entity 
    capitalized even if it is lowercase in the original string '''
    if entity_str.lower() in shorttext_str:
        return entity_str.lower()
    return entity_str
    
make_entities_csv_for_turk()
