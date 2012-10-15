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
    COLUMN_SHORTTEXT_STRING
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
def __get_output_str__(site):
    return "ambiguous entities detected in short texts from "+str(site.siteName)+\
        " written by usernames that exist on both that site and Wikipedia"

def get_ne_candidates_to_evaluate_mturk(site):
    ''' Returns the ambiguous entities mapped to their possible candidates  
    from which humans need to manually choose the correct candidate. '''
    ne_objs = pkl_util.load_pickle(__get_output_str__(site),
                                             __get_ne_cache_path__(site))
    if ne_objs is None:
        return None
    return ne_objs   
    
def build_entities_dataset(shorttext_rows, site):
    
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of users' short texts
    entity_csv_path = __get_entities_csv_path__(site)
    output_str = __get_output_str__(site)
    headers = [__COLUMN_ENTITY_STRING__, COLUMN_SHORTTEXT_ID, COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME]
    entities_in_csv = csv_util.load_or_initialize_csv(entity_csv_path, output_str, headers, __COLUMN_ENTITY_STRING__)
    shorttexts_in_csv = csv_util.get_all_column_values(entity_csv_path, COLUMN_SHORTTEXT_ID)
    
    # Load the cache of ambiguous entity objects
    ne_objs = pkl_util.load_pickle(output_str, __get_ne_cache_path__(site))
    if ne_objs is None:
        ne_objs = []
    
    # Prompt how many users to fetch short texts for
    desired_num_entities = prompt_and_print.prompt_num_entries_to_build(output_str, entities_in_csv)
    
    entities_rows = []
    progress_count = 1
    for shorttext_row in shorttext_rows:
        
        shorttext_id = shorttext_row[0]
        if shorttext_id in shorttexts_in_csv:
            continue # already did entities for this shorttext
        
        try:
            if len(entities_in_csv) >= desired_num_entities:
                # have enough so exit
                break
            
            if progress_count%10==0:
                print "Detecting named entities in short texts posted on "+siteNameStr+\
                " by cross-site usernames... Number of short texts whose entities have been fetched so far: "+\
                str(len(entities_in_csv))
            progress_count = progress_count+1
            
            original_shorttext = shorttext_row[1]
            username = shorttext_row[2]
            
            # get the entities contained in each short text
            # clean the short text before attempting to detect entities in it
            clean_shorttext = text_util.format_shorttext_for_NER(original_shorttext, site)
            
            sf_to_candidates_wikiminer = named_entity_finder.find_candidates_wikipedia_miner(clean_shorttext)
            sf_to_candidates_dbpedia = named_entity_finder.find_candidates_dbpedia(clean_shorttext)
            
            # merge the candidates of the surface forms detected by both services
            sf_to_candidates_union = __merge_sf_maps__(sf_to_candidates_wikiminer, sf_to_candidates_dbpedia)
                
            # now construct a NamedEntity object for each surface form
            for surface_form in sf_to_candidates_union:
                ne_obj = NamedEntity(surface_form,
                                     shorttext_id, original_shorttext,
                                     sf_to_candidates_union[surface_form], 
                                     username, site)
                
                # cache this entity object
                ne_objs.append(ne_obj)
                
                # make a row in the spreadsheet for this entity
                entity_row = [surface_form, 
                              shorttext_id, original_shorttext,
                              username]
                entities_rows.append(entity_row)
                
                # keep track that we'll be adding this entity to the csv
                entities_in_csv.append(surface_form)
        except Exception as st_e:
            raise
            print "Problematic short text ", st_e
            continue # ignore problematic short texts
                
    # update the spreadsheet with any new users' short texts that have been fetched
    csv_util.append_to_spreadsheet(output_str, entity_csv_path, entities_in_csv, entities_rows, False)  
    
    # update the cache of ambiguous surface form objects
    print "Cached a total of "+str(len(ne_objs))+" ambiguous named entities"
    pkl_util.write_pickle(output_str, ne_objs, __get_ne_cache_path__(site))   
    
def __merge_sf_maps__(sf_to_candidates_wikiminer, sf_to_candidates_dbpedia):

    # start with the entities detected by wikiminer
    sf_to_candidates_union = sf_to_candidates_wikiminer 
    
    # then add all the entities detected by dbpedia, 
    # merging candidates for ones also detected by wikiminer
    for surface_form in sf_to_candidates_dbpedia:
        if not surface_form in sf_to_candidates_union:
            # entity not detected by wikiminer, so can just add it to union map
            sf_to_candidates_union[surface_form] = sf_to_candidates_dbpedia[surface_form]
            continue
        
        # otherwise, need to merge the candidate objects...
        
        # start with candidates detected by wikiminer
        union_candidates = sf_to_candidates_union[surface_form]
        
        # then add in missing dbpedia candidates or scores
        dbpedia_candidates = sf_to_candidates_dbpedia[surface_form]
        for cand_title in dbpedia_candidates:
            if not cand_title in union_candidates:
                # candidate not detected by wikiminer, so can just add it
                union_candidates[cand_title] = dbpedia_candidates[cand_title]
                continue
            
            # otherwise, candidate detected by both
            # services so will have a score from each
            cand_obj = union_candidates[cand_title]
            # set its dbpedia score
            cand_obj.dbpedia_score = dbpedia_candidates[cand_title].dbpedia_score
            union_candidates[cand_title] = cand_obj
        
        # update the sf -> candidates
        sf_to_candidates_union[surface_form] = union_candidates  
    return sf_to_candidates_union
