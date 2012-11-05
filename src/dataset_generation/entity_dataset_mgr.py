# -*- coding: utf-8 -*-
"""
Extracts named entities from short texts written by cross-site users on a given site. 
Creates a spreadsheet that contains columns for an entity's id, that entity's text, the id
and text of the short text containing that entity, and the username that wrote that short text. 
Also stores this same information as well as the candidates in a pkl cache for easy access later.

Entity id is constructed by appending its index within its short text's set of entities
after that short text's id. For example, if we have a short text with id 4492 and text
"Bush is the favorite band of Bush, who played for Miami", then there are three entities:
Bush, Bush, and Miami. The entity ids are 4492_0, 4492_1, and 4492_2, respectively. 
This id construction allows us to distinguish between the two separate Bush entities.

Note that only entities that are associated with more than one candidate are included in
the cache because entities with zero or one candidate are not ambiguous so we ignore those.
"""
from CONSTANT_VARIABLES import COLUMN_USERNAME, COLUMN_SHORTTEXT_ID, \
    COLUMN_SHORTTEXT_STRING, COLUMN_ENTITY_ID
from dataset_generation import pkl_util, csv_util, prompt_and_print, \
    crosssite_username_dataset_mgr, nltk_extraction_dataset_mgr
import named_entity_finder
import text_util

__PROMPT_COUNT__ = 10

####### CONSTANT VARIABLES FOR NAMED ENTITIES SPREADSHEET #######
'''Columns for entities spreadsheet'''
__COLUMN_ENTITY_STRING__ =  "entitySurfaceForm"

###########################################################

def __get_entities_csv_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/spreadsheets/entities_'+str(site.siteName)+'.csv'
def __get_ne_cache_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/pickles/surface_form_cache_'+str(site.siteName)+'.pkl'   
def __get_entityless_cache_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/pickles/entityless_shorttexts_cache_'+str(site.siteName)+'.pkl' 
def __get_problematic_cache_path__(site):       
    return '/Users/elizabethmurnane/git/reslve/data/pickles/problematic_shorttexts_cache_'+str(site.siteName)+'.pkl' 
def __get_detected_entities_output_str__(site):
    return "ambiguous entities detected in short texts from "+str(site.siteName)+\
        " written by usernames that exist on both that site and Wikipedia"
__candidate_judgments_output_str__ = "Candidate resources judged by Mechanical Turkers..."
def  __get_candidate_judgments_cache_path__(site):
    return '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/candidate_judgments_cache_'+str(site.siteName)+'.pkl'
__annotator_output_str__ = "Labels (relevant vs not relevant) assigned to candidates by Turker annotators..."
def __get_annotator_cache_path__(site):
    return '/Users/elizabethmurnane/git/reslve/data/mechanical_turk/annotator_decisions_cache_'+str(site.siteName)+'.pkl'

def get_entity_judgements(site):
    judgments = pkl_util.load_pickle(__candidate_judgments_output_str__, 
                                     __get_candidate_judgments_cache_path__(site)) 
    if judgments is None:
        print "No cache of judgments available. Run unresolved_entities_task.py first."
    return judgments
def save_entity_judgements(judgments, site):
    pkl_util.write_pickle(__candidate_judgments_output_str__, judgments, __get_candidate_judgments_cache_path__(site))
    
def get_annotator_decisions(site):
    ''' Loads the cache of turker IDs and their candidate decisions
    sp we can compute measures of inter-annotator agreement. '''
    annotator_decisions = pkl_util.load_pickle(__annotator_output_str__, __get_annotator_cache_path__(site)) 
    if annotator_decisions is None:
        print "No cache of annotator decisions available. Run unresolved_entities_task.py first."
    return annotator_decisions    
def save_annotator_decisions(annotator_decisions, site):
    pkl_util.write_pickle(__annotator_output_str__, annotator_decisions, __get_annotator_cache_path__(site))

def get_num_cached_ne_objs(site):
    ne_objs = pkl_util.load_pickle(__get_detected_entities_output_str__(site),
                                   __get_ne_cache_path__(site))
    if ne_objs is None:
        return 0
    return len(ne_objs)
    
def get_valid_ne_candidates(site):
    ''' Returns the ambiguous entities mapped to their possible candidates  
    from which humans need to manually choose the correct candidate. '''
    ne_objs = pkl_util.load_pickle(__get_detected_entities_output_str__(site),
                                   __get_ne_cache_path__(site))
    if ne_objs is None:
        return None
    return __filter_invalid_entities__(site, ne_objs)   
def __filter_invalid_entities__(site, ne_objs):
    crosssite_usernames = crosssite_username_dataset_mgr.get_confirmed_usernames(site)
    en_lang_users = site.get_en_lang_users(crosssite_usernames)
    valid_entity_cache = nltk_extraction_dataset_mgr.get_nltk_entity_cache(site)
    valid_ne_objs = [ne_obj for ne_obj in ne_objs if ne_obj.is_valid_entity(en_lang_users, valid_entity_cache)]
    return valid_ne_objs

__entityless_output_str__ = "short texts containing no entities"
def get_entityless_shorttexts(site):
    entityless_shorttexts = pkl_util.load_pickle(__entityless_output_str__, __get_entityless_cache_path__(site))
    if entityless_shorttexts is None:
        entityless_shorttexts = [] 
    return entityless_shorttexts
    
__problematic_output_str__ = "problematic short texts"
def get_problematic_shorttexts(site):
    problematic_shorttexts = pkl_util.load_pickle(__problematic_output_str__, __get_problematic_cache_path__(site))
    if problematic_shorttexts is None:
        problematic_shorttexts = []     
    return problematic_shorttexts
            
def build_entities_dataset(shorttext_rows, site):
    
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of users' short texts
    entity_csv_path = __get_entities_csv_path__(site)
    output_str = __get_detected_entities_output_str__(site)
    headers = [COLUMN_ENTITY_ID, __COLUMN_ENTITY_STRING__, COLUMN_SHORTTEXT_ID, COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME]
    entities_in_csv = csv_util.load_or_initialize_csv(entity_csv_path, output_str, headers, COLUMN_ENTITY_ID)
    shorttexts_in_csv = csv_util.get_all_column_values(entity_csv_path, COLUMN_SHORTTEXT_ID)
    print "A total of "+str(len(shorttext_rows))+" short texts available to detect and resolve entities in..."
    
    # Load the cache of ambiguous entity objects
    ne_objs = pkl_util.load_pickle(output_str, __get_ne_cache_path__(site))
    if ne_objs is None:
        ne_objs = []
    
    # Load the cache of short texts that contain no entities
    # and that we don't need to keep querying services with
    entityless_shorttexts = get_entityless_shorttexts(site)
        
    # Load the cache of problematic short texts that we can 
    # go back and look at later..
    problematic_shorttexts = get_problematic_shorttexts(site)
    
    # Prompt how many users to fetch short texts for
    desired_num_entities = prompt_and_print.prompt_num_entries_to_build(output_str, shorttexts_in_csv)
    
    entities_rows = []
    progress_count = 1
    all_shorttexts_done = True
    for shorttext_row in shorttext_rows:
        
        shorttext_id = shorttext_row[0]
        if shorttext_id in shorttexts_in_csv or shorttext_id in entityless_shorttexts or shorttext_id in problematic_shorttexts:
            # already did entities for this shorttext (and either successfully 
            # detected some, successfully detected none, or encountered an error)
            continue
        all_shorttexts_done = False
        
        try:
            if len(entities_in_csv) >= desired_num_entities:
                # have enough so exit
                break
            
            if progress_count%10==0:
                print "Detecting named entities in short texts posted on "+siteNameStr+\
                " by cross-site usernames... Number of short texts whose entities have been fetched so far: \n"+\
                str(len(entities_in_csv))
            progress_count = progress_count+1
            
            original_shorttext = shorttext_row[1]
            username = shorttext_row[2]
            
            # get the entities contained in each short text
            # clean the short text before attempting to detect entities in it
            clean_shorttext = text_util.format_text_for_NER(original_shorttext, site)
            if clean_shorttext=='':
                # whole string was invalid, perhaps a URL or 
                # some other content that gets totally filtered
                problematic_shorttexts.append(shorttext_id)
                continue
            
            detected_entities = named_entity_finder.find_and_construct_named_entities(shorttext_id, original_shorttext, username, site)
            if len(detected_entities)==0:
                entityless_shorttexts.append(shorttext_id)
                
            for ne_obj in detected_entities:
                # cache this entity object
                ne_objs.append(ne_obj)
                
                # make a row in the spreadsheet for this entity
                ne_id = ne_obj.get_entity_id()
                entity_row = [ne_id, ne_obj.surface_form, 
                              shorttext_id, original_shorttext,
                              username]
                entities_rows.append(entity_row)
                
                # keep track that we'll be adding this entity to the csv
                entities_in_csv.append(ne_id)
        except Exception as st_e:
            print "Problematic short text "+str(shorttext_row[1]), st_e
            if 'referenced before assignment' in str(st_e):
                raise # it's a server error so we need to stop 
            problematic_shorttexts.append(shorttext_id)
            continue
                
    # update the spreadsheet with any new users' short texts that have been fetched
    csv_util.append_to_spreadsheet(output_str, entity_csv_path, entities_in_csv, entities_rows, False)  
    
    # update the cache of ambiguous surface form objects
    pkl_util.write_pickle(output_str, ne_objs, __get_ne_cache_path__(site))
    pkl_util.write_pickle(__entityless_output_str__, entityless_shorttexts, __get_entityless_cache_path__(site))
    pkl_util.write_pickle(__problematic_output_str__, problematic_shorttexts, __get_problematic_cache_path__(site))
    print "Cached a total of "+str(len(ne_objs))+" ambiguous named entities"
    if all_shorttexts_done:
        print "Completed detecting and resolving entities in all short texts available."
    else:
        print "More short texts available to detect and resolve entities for."
