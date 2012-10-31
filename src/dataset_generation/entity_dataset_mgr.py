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
from Ambiguous_Entity import NamedEntity
from CONSTANT_VARIABLES import COLUMN_USERNAME, COLUMN_SHORTTEXT_ID, \
    COLUMN_SHORTTEXT_STRING, COLUMN_ENTITY_ID
from dataset_generation import pkl_util, csv_util, prompt_and_print
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
def __get_output_str__(site):
    return "ambiguous entities detected in short texts from "+str(site.siteName)+\
        " written by usernames that exist on both that site and Wikipedia"

def get_ne_candidates_cache(site):
    ''' Returns the ambiguous entities mapped to their possible candidates  
    from which humans need to manually choose the correct candidate. '''
    ne_objs = pkl_util.load_pickle(__get_output_str__(site),
                                   __get_ne_cache_path__(site))
    if ne_objs is None:
        return None
    return ne_objs   

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
    output_str = __get_output_str__(site)
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
            
            # use wikipedia miner and dpedia spotlight to detect
            # named entities and their candidate resources
            try:
                sf_to_candidates_wikiminer = named_entity_finder.find_candidates_wikipedia_miner(clean_shorttext)
            except:
                sf_to_candidates_wikiminer = {}
            try:
                sf_to_candidates_dbpedia = named_entity_finder.find_candidates_dbpedia(clean_shorttext)
            except:
                sf_to_candidates_dbpedia = {}
            
            all_detected_surface_forms = set(sf_to_candidates_wikiminer.keys()).union(sf_to_candidates_dbpedia.keys())
            if len(all_detected_surface_forms)==0:
                entityless_shorttexts.append(shorttext_id)
            
            # now construct a NamedEntity object for each detected surface form
            for surface_form in all_detected_surface_forms:
                ne_obj = NamedEntity(surface_form,
                                     shorttext_id, original_shorttext,
                                     username, site)    
                
                # set the NamedEntity's baseline candidate rankings 
                if surface_form in sf_to_candidates_wikiminer:
                    ne_obj.set_wikipedia_miner_ranking(sf_to_candidates_wikiminer[surface_form])
                if surface_form in sf_to_candidates_dbpedia:
                    ne_obj.set_dbpedia_spotlight_ranking(sf_to_candidates_dbpedia[surface_form])
                
                # cache this entity object
                ne_objs.append(ne_obj)
                
                # make a row in the spreadsheet for this entity
                ne_id = ne_obj.get_entity_id()
                entity_row = [ne_id, surface_form, 
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
