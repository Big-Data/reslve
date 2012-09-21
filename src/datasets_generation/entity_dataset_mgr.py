# -*- coding: utf-8 -*-
"""
Extracts named entities from short texts written by cross-site users on a given site. 
Creates a spreadsheet that contains columns for an entity's id, that entity's text, the id
and text of the short text containing that entity, and the username that wrote that short text. 

Entity id is constructed by appending its index within its short text's set of entities
after that short text's id. For example, if we have a short text with id 4492 and text
"Bush is the favorite band of Bush, who played for Miami", then there are three entities:
Bush, Bush, and Miami. The entity ids are 4492_0, 4492_1, and 4492_2, respectively. 
This id construction allows us to distinguish between the two separate Bush entities.
"""
from CONSTANT_VARIABLES import COLUMN_USERNAME, COLUMN_SHORTTEXT_ID, \
    COLUMN_SHORTTEXT_STRING
from datasets_generation import csv_util, prompt_and_print
import named_entity_finder
import unicodedata

__PROMPT_COUNT__ = 10

####### CONSTANT VARIABLES FOR NAMED ENTITIES SPREADSHEET #######
'''Columns for entities spreadsheet'''
__COLUMN_ENTITY_ID__ = "entityID"
__COLUMN_ENTITY_STRING__ =  "entityTextString"

###########################################################

def __get_entity_csv_path__(site):
    ''' @param site: a Site object '''
    return 'datasets/spreadsheets/entities_'+str(site.siteName)+'.csv'

def build_entities_dataset(shorttext_rows, site):
    
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of users' short texts
    entity_csv_path = __get_entity_csv_path__(site)
    csv_string = "entities detected in short texts from "+siteNameStr+\
    " written by usernames that exist on both that site and Wikipedia"
    headers = [__COLUMN_ENTITY_ID__, __COLUMN_ENTITY_STRING__, COLUMN_SHORTTEXT_ID, COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME]
    entities_in_csv = csv_util.load_or_initialize_csv(entity_csv_path, csv_string, headers, __COLUMN_ENTITY_ID__)
    shorttexts_in_csv = csv_util.get_all_column_values(entity_csv_path, COLUMN_SHORTTEXT_ID)
    
    # Prompt how many users to fetch short texts for
    desired_num_entities = prompt_and_print.prompt_num_entries_to_build(csv_string, entities_in_csv)
    
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
                " by cross-site usernames... Number short texts whose entities have been fetched so far: "+str(progress_count)
            progress_count = progress_count+1
            
            shorttext_string = shorttext_row[1]
            username = shorttext_row[2]
            
            # get the entities contained in each short text
            surface_forms_to_candidates = named_entity_finder.find_candidates_wikipedia_miner(shorttext_string)
            index_count = 0
            for named_entity_string in surface_forms_to_candidates:
                named_entity_string = unicodedata.normalize('NFKD', named_entity_string).encode('ascii','ignore').encode('utf-8')
                try:
                    entity_id = str(shorttext_id)+'_'+str(index_count)
                    entity_row = [entity_id, named_entity_string.decode('utf-8'), 
                                  shorttext_id, shorttext_string.decode('utf-8'),
                                  username]
                    entities_rows.append(entity_row)
                    
                    # keep track that we'll be adding this entity to the csv
                    entities_in_csv.append(entity_id)
                    
                    # increment the entity's index within 
                    # this short text's set of all entities
                    index_count = index_count + 1
                except:
                    raise # ignore problematic entities
        except:
            raise # ignore problematic short texts
                
    # update the spreadsheet with any new users' short texts that have been fetched
    csv_util.append_to_spreadsheet(csv_string, entity_csv_path, entities_in_csv, entities_rows, False)  
        