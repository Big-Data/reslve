from Ambiguous_Entity import NamedEntity
from CONSTANT_VARIABLES import COLUMN_ENTITY_ID, COLUMN_SHORTTEXT_ID, \
    COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME
from dataset_generation import csv_util, pkl_util, \
    crosssite_username_dataset_mgr
from dataset_generation.entity_dataset_mgr import __COLUMN_ENTITY_STRING__
import named_entity_finder
import random
import text_util

''' Builds a spreadsheet and cache of entities from users that are confirmed
to *NOT* be the same person on Wikipedia and the given site. Since in this case
the Wikipedia edits would not serve as personally relevant background
information to the twitter user (different people), the performance of our algorithms
would be expected to be worse and we can use this performance as a baseline. '''

def __get_nonmatch_entities_csv_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/spreadsheets/entities_'+str(site.siteName)+'_nonmatch_baseline.csv'    
def __get_nonmatch_ne_cache_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/pickles/nonmatch_baseline_NamedEntity_cache_'+str(site.siteName)+'.pkl'      
    
def build_entities_dataset(site):
    
    # Load or create/initialize the spreadsheet of users' short texts
    entity_csv_path = __get_nonmatch_entities_csv_path__(site)
    output_str = 'entities in short texts written by nonmatch users'
    headers = [COLUMN_ENTITY_ID, __COLUMN_ENTITY_STRING__, COLUMN_SHORTTEXT_ID, COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME]
    entities_in_csv = csv_util.load_or_initialize_csv(entity_csv_path, output_str, headers, COLUMN_ENTITY_ID)
    
    # Load the cache of ambiguous entity objects
    nonmatch_ne_objs = pkl_util.load_pickle(output_str, __get_nonmatch_ne_cache_path__(site))
    if nonmatch_ne_objs is None:
        nonmatch_ne_objs = []
    
    entities_rows = []

    confirmed_nonmatches = crosssite_username_dataset_mgr.get_confirmed_nonmatch_usernames(site)
    subset_num = 50
    print str(len(confirmed_nonmatches))+" usernames confirmed to not belong to single person according to turkers."
    if len(confirmed_nonmatches) < subset_num:
        print "Not enough confirmed non-matches. Run unconfirmed_usernames_task.py to update cross-site username spreadsheet first."
        return
    subset_confirmed_nonmatches = random.sample(confirmed_nonmatches, )
    for username in subset_confirmed_nonmatches:
        shorttexts_response = site.get_user_short_texts(username) # fetch from site
        user_shorttexts = shorttexts_response[site.get_shorttext_response_key()]
        for shorttext_id in user_shorttexts:
            shorttext_text = user_shorttexts[shorttext_id].decode('utf-8')
            clean_shorttext = text_util.format_text_for_NER(shorttext_text, site)
    
            # use wikipedia miner and dpedia spotlight to detect
            # named entities and their candidate resources
            sf_to_candidates_wikiminer = named_entity_finder.find_candidates_wikipedia_miner(clean_shorttext)
            sf_to_candidates_dbpedia = named_entity_finder.find_candidates_dbpedia(clean_shorttext)
            all_detected_surface_forms = set(sf_to_candidates_wikiminer.keys()).union(sf_to_candidates_dbpedia.keys())
            
            # now construct a NamedEntity object for each detected surface form
            for surface_form in all_detected_surface_forms:
                ne_obj = NamedEntity(surface_form,
                                     shorttext_id, shorttext_text,
                                     username, site)    
                
                # set the NamedEntity's baseline candidate rankings 
                if surface_form in sf_to_candidates_wikiminer:
                    ne_obj.set_wikipedia_miner_ranking(sf_to_candidates_wikiminer[surface_form])
                if surface_form in sf_to_candidates_dbpedia:
                    ne_obj.set_dbpedia_spotlight_ranking(sf_to_candidates_dbpedia[surface_form])
                
                # cache this entity object
                nonmatch_ne_objs.append(ne_obj)
                
                # make a row in the spreadsheet for this entity
                ne_id = ne_obj.get_entity_id()
                entity_row = [ne_id, surface_form, 
                              shorttext_id, shorttext_text,
                              username]
                entities_rows.append(entity_row)
                
                # keep track that we'll be adding this entity to the csv
                entities_in_csv.append(ne_id)
                
    # update the spreadsheet with any new users' short texts that have been fetched
    csv_util.append_to_spreadsheet(output_str, entity_csv_path, entities_in_csv, entities_rows, False)  
    
    # update the cache of ambiguous surface form objects
    pkl_util.write_pickle(output_str, nonmatch_ne_objs, __get_nonmatch_ne_cache_path__(site))
