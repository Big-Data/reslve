"""
Queries the given site for short texts posted by cross-site usernames.

Saves this information in a spreadsheet with columns for the 
short text id, its text string, and the username who posted it.
"""
from CONSTANT_VARIABLES import COLUMN_USERNAME, COLUMN_SHORTTEXT_ID, \
    COLUMN_SHORTTEXT_STRING
from dataset_generation import csv_util, prompt_and_print

__PROMPT_COUNT__ = 10

def __get_shorttexts_csv_path__(site):
    ''' @param site: a Site object '''
    return 'data/spreadsheets/shorttexts_'+str(site.siteName)+'.csv'

def build_shorttexts_dataset(crosssite_usernames, site):
    
    siteNameStr = str(site.siteName)
    
    # Load or create/initialize the spreadsheet of users' short texts
    shorttexts_csv_path = __get_shorttexts_csv_path__(site)
    csv_string = "cross-site (Wikipedia and "+siteNameStr+") users' short texts"
    headers = [COLUMN_SHORTTEXT_ID, COLUMN_SHORTTEXT_STRING, COLUMN_USERNAME]
    shorttexts_in_csv = csv_util.load_or_initialize_csv(shorttexts_csv_path, csv_string, headers, COLUMN_SHORTTEXT_ID)
    usernames_in_csv = list(set(csv_util.get_all_column_values(shorttexts_csv_path, COLUMN_USERNAME)))
    
    # only need to fetch the short texts for usernames that we haven't already done
    users_todo = [u for u in crosssite_usernames if u not in usernames_in_csv]
    if len(users_todo)==0:
        print "Short texts fetched and stored for all "+\
        str(len(usernames_in_csv))+" confirmed cross-site editors. Exiting."
        return 
    
    print str(len(crosssite_usernames))+" cross-site usernames total, and "+\
    str(len(users_todo))+" users not yet in spreadsheet of short texts "
    
    # Prompt how many users to fetch short texts for
    desired_num_users = prompt_and_print.prompt_num_entries_to_build(csv_string, usernames_in_csv)
    num_to_append = desired_num_users - len(usernames_in_csv)
    if len(users_todo) < num_to_append:
        print "Only "+str(len(users_todo))+" cross-site usernames available. If you want "+\
        "want "+str(desired_num_users)+" total users' short texts in the short text csv, you'll "+\
        "have to re-run script and choose to first fetch more cross-site usernames."
    
    shorttexts_rows = []
    progress_count = 1
    for username in users_todo:
        
        try:
            if len(usernames_in_csv) >= desired_num_users:
                # have enough so exit
                break
            
            if progress_count%10==0:
                print "Querying for short texts posted on "+siteNameStr+" by cross-site usernames..."+\
                " Number usernames whose short texts have been fetched so far: "+str(progress_count)
            progress_count = progress_count+1
    
            # For the usernames that have been confirmed to belong to the same
            # individual person on Wikipedia and the given site, get the short
            # texts those users have written on that site
            shorttexts_response = site.get_user_short_texts(username) # fetch from site
            user_shorttexts = shorttexts_response[site.get_shorttext_response_key()]
            for shorttext_id in user_shorttexts:
                try:
                    # create row for user's short texts
                    shorttext_text = user_shorttexts[shorttext_id].decode('utf-8')
                    shorttext_row = [shorttext_id, shorttext_text, username]
                    shorttexts_rows.append(shorttext_row)
                except:
                    continue # ignore problematic short texts
                
            # keep track that we'll be adding this username to the csv
            usernames_in_csv.append(username)
                
            # also check whether rate limit reached
            rate_limited = shorttexts_response[site.get_rate_limit_key()]
            if rate_limited:
                break # reached rate limit, so break        
        except:
            continue # ignore problematic users
                
    # update the spreadsheet with any new users' short texts that have been fetched
    csv_util.append_to_spreadsheet(csv_string, shorttexts_csv_path, shorttexts_in_csv, shorttexts_rows) 

def get_shorttext_rows(site):
    shorttext_csv_path = __get_shorttexts_csv_path__(site)
    return csv_util.query_csv_for_rows(shorttext_csv_path)
        