from dataset_generation import entity_dataset_mgr
from short_text_sources import short_text_websites
import random

twitter_site = short_text_websites.get_twitter_site()
entities_to_evaluate = entity_dataset_mgr.get_ne_candidates_to_evaluate_mturk(twitter_site, '../')
if entities_to_evaluate is None:
    print "No ambiguous entities + candidates in cache. Run all_datasets_build "+\
    "script and choose to first fetch and store more entities from short texts."
else:
    
    # Some instructions for the task
    for surface_form_obj in entities_to_evaluate:
        
        # Tell turker to read the short text
        shorttext_str = surface_form_obj.shorttext_str
        print "\nRead the following piece of text: \""+str(shorttext_str)+"\""
        
        # Tell turker to look at entity and choose correct candidate
        entity_str = surface_form_obj.entity_str
        print "From the below set of choices, please select the correct intended meaning of the term \""\
        +str(entity_str)+"\""
        
        print "Note: You can check the Wikipedia page of a choice if it will help you understand its meaning better."
        print "Choices:"
        # shuffle candidates so that they don't appear
        # in wikiminer's ranking order and bias the turker
        candidates = surface_form_obj.get_candidates()
        random.shuffle(candidates)
        for candidate in candidates:
            print str(candidate)+\
            " (http://en.wikipedia.org/wiki/"+str(candidate).replace(' ','_')+")"
