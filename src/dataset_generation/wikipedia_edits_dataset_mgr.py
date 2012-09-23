"""
Queries Wikipedia for the article edit history for each username in the
cross-site username spreadsheet (these usernames have been confirmed to belong 
to a single individual. 

Saves this information in a spreadsheet with columns for the username, the 
edited article page ID, and the number of edits that user has made on that page.
"""
from CONSTANT_VARIABLES import COLUMN_USERNAME
from dataset_generation import csv_util, prompt_and_print, pkl_util
from wikipedia import wikipedia_api_util

__PROMPT_COUNT__ = 10

####### CONSTANT VARIABLES FOR WIKIPEDIA EDITS SPREADSHEET #######
'''Columns for edits spreadsheet'''
__COLUMN_ARTICLE_ID__ = "articleID"
__COLUMN_NUM_EDITS__ =  "numberEditsByUser"

###########################################################

__edits_csv_path__ = '../data/spreadsheets/wikipedia_edits.csv'
__edits_cache_path__ = '../data/pickles/wikipedia_edits_cache.pkl'    

def get_edits_by_user(username):
    editor_names_to_edits_cache = pkl_util.load_pickle("Wikipedia editor usernames to their edited pages+counts",
                                                       __edits_cache_path__)
    try:
        return editor_names_to_edits_cache[username]
    except:
        return []

def build_wikipedia_edits_dataset(crosssite_usernames, site):
    
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of users' wikipedia edits
    edits_csv_path = __edits_csv_path__
    csv_string = 'Wikipedia edits made by usernames that also exist on '+siteNameStr
    headers = [COLUMN_USERNAME, __COLUMN_ARTICLE_ID__, __COLUMN_NUM_EDITS__]
    usernames_in_csv = csv_util.load_or_initialize_csv(edits_csv_path, csv_string, headers, COLUMN_USERNAME)
    
    # Load the cache of edits, a dict: { username -> {edited page -> num edits } }
    edits_cache_path = __edits_cache_path__
    editor_names_to_edits_cache = pkl_util.load_pickle("Wikipedia editor usernames to their edited pages+counts",
                                                       edits_cache_path)
    if editor_names_to_edits_cache is None:
        editor_names_to_edits_cache = {}

    # only need to fetch the edits for usernames that we haven't already done
    editors_todo = [u for u in crosssite_usernames if u not in usernames_in_csv]
    
    # Exit if all available names are done
    if len(editors_todo)==0:
        print "Wikipedia edit data fetched and stored for all "+\
        str(len(crosssite_usernames))+" confirmed cross-site editors. Exiting."
        return 
    
    print str(len(crosssite_usernames))+" cross-site editors total, and "+\
    str(len(editors_todo))+" editors not yet in spreadsheet of edits "
    
    # Prompt how many users to fetch edits for
    desired_num_editors = prompt_and_print.prompt_num_entries_to_build(csv_string, usernames_in_csv)
    num_to_append = desired_num_editors - len(usernames_in_csv)
    if len(editors_todo) < num_to_append:
        print "Only "+str(len(editors_todo))+" cross-site usernames available. If you want "+\
        "want "+str(desired_num_editors)+" total editors' edits in the edits csv, you'll have to "+\
        "re-run script and choose to first fetch more cross-site usernames."
    
    edits_rows = []
    prompt_count = 0
    progress_count = 1
    for username in editors_todo:
        
        if len(usernames_in_csv) >= desired_num_editors:
            # have enough so exit
            break
        
        '''
        # Intermittently prompt user whether to continue fetching matching usernames or exit script
        if prompt_count >= __PROMPT_COUNT__:
            continue_searching = prompt_and_print.prompt_continue_building(csv_string, usernames_in_csv, desired_num_editors)
            if not continue_searching:
                break
            prompt_count = 0 # reset count
        prompt_count = prompt_count + 1
        '''
        
        if progress_count%10==0:
            print "Querying for pages edited by cross site usernames... Number "+\
            "usernames whose edits have been fetched so far: "+str(progress_count)
        progress_count = progress_count+1
        
        user_edits = wikipedia_api_util.query_usercontribs(username, False)
        for article_id in user_edits:
            num_times_edited = user_edits[article_id]
            edits_row = [username, article_id, num_times_edited]
            edits_rows.append(edits_row)
            
        # keep track that we'll be adding this username to the csv
        usernames_in_csv.append(username)
        editor_names_to_edits_cache[username] = user_edits # add that user+edits to cache
                
    # update the spreadsheet with any new editors' edits that have been fetched
    csv_util.append_to_spreadsheet(csv_string, edits_csv_path, usernames_in_csv, edits_rows, False)  
        
    # update the edit mapping cache
    pkl_util.write_pickle("user edits to file...", 
                          editor_names_to_edits_cache, edits_cache_path)
        