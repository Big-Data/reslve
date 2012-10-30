"""
Handles building the cross-site username datasets (csv and 
pkl caches) as well as accessing them to look up values. 

To build the cross-site username dataset:
Makes queries to wikipedia for active usernames and for each attempts to find 
an account that is also active on the given site and has the same username. 
Creates columns for the username and whether the account on Wikipedia and the
given site actually belong to the same individual person.

The task of determining whether a username belongs to the same person on 
Wikipedia and on Twitter is left up to human evaluators (ie Mechanical 
Turkers), so for each evaluator the spreadsheet contains a column of the 
form "isSameIndividual (Annotator_ID)". 
By default, the entries in this column are "UNCONFIRMED", ie have not 
yet been evaluated by a human.
"""
from CONSTANT_VARIABLES import COLUMN_USERNAME
from dataset_generation import csv_util, prompt_and_print, pkl_util
from wikipedia import wikipedia_api_util

__PROMPT_COUNT__ = 10

####### CONSTANT VARIABLES FOR USERNAME SPREADSHEET #######
'''Columns for username spreadsheet'''
__COLUMN_SAME_INDIVIDUAL__ = 'isSameIndividual'

''' cell values for SAME_INDIVIDUAL column that indicate whether
a human evaluator has judged whether accounts with the same 
username to actually correspond to the same individual or not. '''
# evaluated by a human and judged to correspond to same individual:
__VALUE_CONFIRMED_POSITIVE__ = 'CONFIRMED_POSITIVE' 
# evaluated by a human and judged to correspond to different individuals:
__VALUE_CONFIRMED_NEGATIVE__ = 'CONFIRMED_NEGATIVE' 
# evaluated by a human and unable to judge whether 
# accounts correspond to same individual or not:
__VALUE_CONFIRMED_UNKNOWN__ = 'CONFIRMED_UNKNOWN' 
# if not evaluated by any human
__VALUE_UNCONFIRMED__ = 'UNCONFIRMED' 
###########################################################

def get_confirmed_usernames(site):
    ''' Returns the usernames that humans have manually confirmed belong 
    to the same individual user on Wikipedia and the given site. '''
    return __get_usernames__(site, __VALUE_CONFIRMED_POSITIVE__)
def get_confirmed_nonmatch_usernames(site):
    ''' Returns the usernames that humans have manually confirmed DO NOT 
    belong to the same individual user on Wikipedia and the given site. '''
    return __get_usernames__(site, __VALUE_CONFIRMED_NEGATIVE__) 
def __get_usernames__(site, confirm_value):
    usernames_csv_path = __get_usernames_csv_path__(site)
    return csv_util.query_csv_for_rows_with_value(usernames_csv_path, 
                                                  COLUMN_USERNAME, 
                                                  __COLUMN_SAME_INDIVIDUAL__, 
                                                confirm_value)    

def get_usernames_to_evaluate_mturk(site):
    ''' Returns the usernames that humans need to manually confirm belong 
    to the same individual user on Wikipedia and the given site. '''
    usernames_csv_path = __get_usernames_csv_path__(site)
    need_to_be_evaluated = csv_util.query_csv_for_rows_with_value(usernames_csv_path, 
                                                                  COLUMN_USERNAME,
                                                                  __COLUMN_SAME_INDIVIDUAL__,
                                                                  __VALUE_UNCONFIRMED__)
    return need_to_be_evaluated

def update_confirmed_positive_usernames(site, usernames):
    ''' Updates the COLUMN_SAME_INDIVIDUAL cell value to __VALUE_CONFIRMED_POSITIVE__ 
    for each of the given usernames confirmed by Mechanical Turk workers 
    to belong to the same individual. ''' 
    __update_confirmed_usernames__(site, usernames, __VALUE_CONFIRMED_POSITIVE__)
def update_confirmed_negative_usernames(site, usernames):
    ''' Updates the COLUMN_SAME_INDIVIDUAL cell value to __VALUE_CONFIRMED_NEGATIVE__ 
    for each of the given usernames confirmed by Mechanical Turk workers 
    to *NOT* belong to the same individual. ''' 
    __update_confirmed_usernames__(site, usernames, __VALUE_CONFIRMED_NEGATIVE__)
def __update_confirmed_usernames__(site, confirmed_usernames, confirmed_value):
    usernames_csv_path = __get_usernames_csv_path__(site)
    headers = csv_util.query_csv_for_headers(usernames_csv_path)
    
    username_col_index = headers.index(COLUMN_USERNAME)
    confirmed_col_index = headers.index(__COLUMN_SAME_INDIVIDUAL__)
    
    updated_rows = []
    rows = csv_util.query_csv_for_rows(usernames_csv_path, False)
    for row in rows:
        if row[username_col_index] in confirmed_usernames:
            row[confirmed_col_index] = confirmed_value
        updated_rows.append(row)
    csv_util.write_to_spreadsheet(usernames_csv_path, updated_rows)

def __get_usernames_csv_path__(site):
    ''' @param site: a Site object '''
    return '/Users/elizabethmurnane/git/reslve/data/spreadsheets/cross-site-usernames_'+str(site.siteName)+'.csv'
def __get_nonexistent_usernames_cache_path__(site):
    ''' @param site: a Site object
        @return: the cache of usernames that do no exist on the given site '''
    return '/Users/elizabethmurnane/git/reslve/data/pickles/nonexistent_usernames_on_'+str(site.siteName)+'.pkl'
__wikipedia_editors_cache_path__ = '../data/pickles/wikipedia_editors_cache.pkl'

def build_wikipedia_editor_username_cache():
    ''' Fetches large numbers of active Wikipedia editors who have made edits 
    recently and stores them in a cache, which we can access while attempting
    to find usernames that exist on both Wikipedia and a short text source site. 
    (The occurrence of such cross-site username matces may be low, so we want 
    to have a large cache of Wikipedia editors to draw upon).
    The cache is a mapping of { username -> { edited page -> number of edits on page } } '''
    
    # Load the Wikipedia usernames+edits cache
    output_str = "Wikipedia editor usernames and their edited pages..."
    editor_usernames = pkl_util.load_pickle(output_str, 
                                            __wikipedia_editors_cache_path__)
    if editor_usernames is None:
        editor_usernames = []

    # Prompt how many Wikipedia usernames to fetch and query Wikipedia until retrieved that many
    desired_num_editors = prompt_and_print.prompt_num_entries_to_build("active Wikipedia editors", 
                                                                       editor_usernames)
    pre_fetch_len = len(editor_usernames)
    wikipedia_api_util.query_editors_of_recentchanges(desired_num_editors, editor_usernames)
    print "Fetched "+str(len(editor_usernames)-pre_fetch_len)+" more recent and active Wikipedia editors"
    
    # make sure all usernames are lowercase
    editor_usernames = [u.lower() for u in editor_usernames]
    
    # Update cache
    print "Cached a total of "+str(len(editor_usernames))+" Wikipedia editor usernames"
    pkl_util.write_pickle(output_str, editor_usernames, __wikipedia_editors_cache_path__)
    
    
def build_crosssite_username_dataset(site):
    ''' Searches the given site for the Wikipedia editor usernames we have previously cached.
    Does so until have a sufficient set of unique users who have both active Wikipedia accounts 
    and active accounts on the given site. Saves those users in a csv file and a pkl cache 
    and also writes to cache the usernames that are determined to NOT exist on the given 
    site so we don't bother searching for them again in the future. 
    @param site: Should be a Site object 
    '''
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of usernames
    usernames_csv_path = __get_usernames_csv_path__(site)
    csv_string = 'usernames that exist on both Wikipedia and '+siteNameStr
    headers = [COLUMN_USERNAME, __COLUMN_SAME_INDIVIDUAL__]
    usernames_in_csv = csv_util.load_or_initialize_csv(usernames_csv_path, csv_string, headers, COLUMN_USERNAME)

    # Load the caches of Wikipedia usernames:
    editor_names_cache = pkl_util.load_pickle("Wikipedia editor usernames",
                                          __wikipedia_editors_cache_path__)
    editor_usernames = [] if (editor_names_cache is None) else editor_names_cache
    # editor usernames that do NOT exist on the given site
    nonexistent_usernames_path = __get_nonexistent_usernames_cache_path__(site)
    nonexistent_usernames_cache = pkl_util.load_pickle("Wikipedia usernames that do NOT exist on "+siteNameStr+"...", 
                                                       nonexistent_usernames_path)
    if nonexistent_usernames_cache==None:
        nonexistent_usernames_cache = []
    
    # only need to analyze those usernames that we haven't 
    # already determined do or do not exist on given site
    usernames_todo = __get_remaining_todo__(editor_usernames, 
                                        [usernames_in_csv, nonexistent_usernames_cache])
    
    # Prompt how many matching usernames to fetch from the given site  
    desired_num_usernames = prompt_and_print.prompt_num_entries_to_build(csv_string, usernames_in_csv)
    num_to_append = desired_num_usernames - len(usernames_in_csv)
    if len(usernames_todo) < num_to_append:
        print "Only "+str(len(usernames_todo))+" unanalyzed Wikipedia usernames in cache. If you "+\
        "want "+str(desired_num_usernames)+" total in the cross-site usernames csv, you'll have to "+\
        "re-run script and choose to first fetch more Wikipedia editor usernames."
    
    prompt_count = 0
    while(len(usernames_in_csv)<desired_num_usernames and len(usernames_todo)>0):
        
        # Intermittently prompt user whether to continue fetching matching usernames or exit script
        if prompt_count >= __PROMPT_COUNT__:
            continue_searching = prompt_and_print.prompt_continue_building(csv_string, usernames_in_csv, desired_num_usernames)
            if not continue_searching:
                break
            prompt_count = 0 # reset count
        prompt_count = prompt_count + 1
        
        # get lists of usernames that do or do not also exist on the given site
        match_response = site.fetching_existence_status(usernames_todo, desired_num_usernames)
        existing = match_response[site.get_existing_response_key()]
        nonexisting = match_response[site.get_nonexisting_response_key()]
        
        print "Found "+str(len(existing))+" existing and active usernames on "+siteNameStr

        # update the spreadsheet with any new usernames that have been fetched
        existing_rows = [[username, __VALUE_UNCONFIRMED__] for username in existing]
        csv_util.append_to_spreadsheet(csv_string, usernames_csv_path, 
                                       usernames_in_csv, existing_rows)
        # and update the list of usernames in the csv so we know how 
        # many more we still need to fetch to reach the desired num
        usernames_in_csv.extend(existing)
    
        # Also update the cache of Wikipedia usernames that do NOT exist on the given site
        nonexistent_usernames_cache.extend(nonexisting)
        nonexistent_write_str = "usernames that DO NOT exist on both Wikipedia and "+siteNameStr+"..."
        pkl_util.write_pickle(nonexistent_write_str, nonexistent_usernames_cache, nonexistent_usernames_path)
        
        # remove any usernames that we now determined do not exist on given site
        usernames_todo = __get_remaining_todo__(usernames_todo, [existing, nonexistent_usernames_cache])
      
        rate_limited = match_response[site.get_rate_limit_key()]
        if rate_limited:
            break # reached rate limit, so break
        
def __get_remaining_todo__(full, lists_of_analyzed):
    already_analyzed = []
    for loau in lists_of_analyzed:
        already_analyzed.extend(loau)
    remaining_todo = [u for u in full if u not in already_analyzed]
    return remaining_todo
