from datasets_generation import prompt_and_print, crosssite_username_dataset_mgr, \
    wikipedia_edits_dataset_mgr, short_text_dataset_mgr, entity_dataset_mgr

def build_all_datasets():
    
    # Build up the cache of Wikipedia editor usernames
    if prompt_and_print.prompt_for_build_wikipedia_username_cache():
        crosssite_username_dataset_mgr.build_wikipedia_editor_username_cache()
        
    # Prompt to ask from which site we want to build a dataset
    site = prompt_and_print.prompt_for_site()
    
    # Build up the spreadsheet of usernames that
    # on exist both Wikipedia and the passed site
    if prompt_and_print.prompt_for_build_username_csv():
        crosssite_username_dataset_mgr.build_crosssite_username_dataset(site)
        
    # Get the confirmed usernames from the spreadsheet since these will 
    # be the usernames from which Wikipedia edits and short texts are fetched 
    crosssite_usernames = crosssite_username_dataset_mgr.get_confirmed_usernames(site)
    
    # Build the spreadsheet of articles that
    # these usernames have edited on Wikipedia
    if prompt_and_print.prompt_for_build_edits_csv():
        wikipedia_edits_dataset_mgr.build_wikipedia_edits_dataset(crosssite_usernames, site)
        
    # Build the spreadsheet of short texts that
    # these usernames have posted on the input site
    if prompt_and_print.prompt_for_build_shorttexts_csv(site):
        short_text_dataset_mgr.build_shorttexts_dataset(crosssite_usernames, site)
     
    # Get the shorttexts fetched from the given site   
    shorttext_rows = short_text_dataset_mgr.get_shorttext_rows(site)
        
    # Build the spreadsheet of named entities that are
    # contained within these short texts on the given site
    if prompt_and_print.prompt_for_build_entity_csv(site):
        entity_dataset_mgr.build_entities_dataset(shorttext_rows, site) 
        
build_all_datasets()
