""" Functions that prompt the user for input and
functions that print output to the console """
from short_text_sources import short_text_websites

def prompt_for_continue_building():
    prompt_input = raw_input("Continue building datasets or Quit? (C to continue, Q to quit): ")
    return 'C'==prompt_input or 'c'==prompt_input

def prompt_for_site():
    site_input = raw_input('Work with (A) Twitter or (B) Flickr? (Enter A or B): ')
    site = {'A':short_text_websites.get_twitter_site(), 'B':'SITE_FLICKR'}[site_input]
    return site

def __prompt_for_build__(prompt_str):
    prompt_input = raw_input(prompt_str)
    return 'Y'==prompt_input or 'y'==prompt_input

def prompt_for_build_wikipedia_username_cache():
    return __prompt_for_build__("Create or update pkl cache of Wikipedia editor usernames? (Y/N): ")

def prompt_for_build_username_csv():
    return __prompt_for_build__("Create or update CSV of cross-site usernames? (Y/N): ")

def prompt_for_build_edits_csv():
    return __prompt_for_build__("Create or update CSV of Wikipedia articles "+\
                                "edited by cross-site usernames? (Y/N): ")

def prompt_for_build_shorttexts_csv(site):    
    return __prompt_for_build__("Create or update CSV of short texts posted on "+\
                                str(site.siteName)+" by cross-site usernames? (Y/N): ")
    
def prompt_for_build_entity_csv(site):
    return __prompt_for_build__("Create or update CSV of entities detected in short texts posted on "+\
                                str(site.siteName)+" by cross-site usernames? (Y/N): ")
    
def prompt_num_entries_to_build(output_string, entries_in_file):
    print str(len(entries_in_file))+" entries in file of "+output_string  
    desired_num = int(raw_input("Total number of entries desired? (Enter number): "))
    __print_remaining__(output_string, entries_in_file, desired_num)
    return desired_num

def prompt_continue_building(output_string, curr_entries, desired_num):
    __print_remaining__(output_string, curr_entries, desired_num)
    continue_scoring = raw_input("Continue appending "+output_string+"? (Y/N):")
    return 'Y'==continue_scoring or 'y'==continue_scoring

def __print_remaining__(output_string, curr_entries, desired_num):
    remaining =  max(0, desired_num - len(curr_entries))
    if 0==remaining:
        print "Done - "+str(desired_num)+" entries in "+output_string
    else:
        print "Still need to append "+str(remaining)+" more "+output_string
