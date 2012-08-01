"""
Makes queries to wikipedia and twitter for user accounts. Collects usernames for 
which both an active wikipedia account and an active twitter account exist until 
a total of 1500 such usernames is retrieved. Writes these usernames to a CSV file, 
along with a column that specifies whether the username actually belongs to the 
same single person on wikipedia and on twitter. Currently, this value is "unknown" 
for every username because we need to manually evaluate the likelihood, perhaps 
using Mechanical Turk.
"""

from util import wiki_util
from spreadsheet_labels import USERNAME_COLUMN, MATCH_COLUMN, MATCH_UNKNOWN
import account_matching
import csv
import pickle
import urllib2

# Collect this many usernames 
__users_sample_size__ = 1000

# For now, piloting with "active" users only 
# ("active": n>=100 contributions on wikipedia/twitter)
__min_edits__ = 100
__min_tweets__ = 100

try:
    usernames_file = open('pickles/usernames.pkl', 'rb')
    users = pickle.load(usernames_file)
except:
    users = set()

# Fetch random editors from wikipedia until have a set of unique users
# who have both active wikipedia accounts and active twitter accounts
while len(users) < __users_sample_size__:
    print "Fetching users..."
    print "Current sample size: "+str(len(users))+" users"
    try:
        wiki_editors = []
        while(len(wiki_editors) < 100):
            try:
                rand_user_req_url = 'http://en.wikipedia.org/wiki/Special:Random/User'
                req = urllib2.Request(rand_user_req_url, headers={'User-Agent' : "Browser"})
                user_url_str = str(urllib2.urlopen(req).geturl())
                user_namespace = 'User:'
                pos = user_url_str.find(user_namespace)
                if pos==-1:
                    continue
                
                username = user_url_str[pos+len(user_namespace):]
                extra_path = '/'
                extra_pos = username.find(extra_path)
                if extra_pos!=-1:
                    username = username[0:extra_pos]
                    
                # Only including "active" wikipedia users, ie those who 
                # have made a minimum number of non-trivial edits
                if not wiki_util.is_active_user(username, __min_edits__):
                    continue
                
                wiki_editors.append(username)
            except:
                continue
                    
        # Once have 100 (the max allowed for twitter batch lookups) wikipedia users,
        # do a batch lookup on twitter for active accounts with matching usernames
        twitter_accounts = account_matching.find_twitter_matches(wiki_editors, __min_tweets__)
        users.update(twitter_accounts)
    except:
        continue
if len(users) >= __users_sample_size__:
    print "Collected sample of "+str(len(users))+" users"

# pickle usernames
usernames_pickle = open('pickles/usernames.pkl', 'wb')
pickle.dump(users, usernames_pickle)
usernames_pickle.close()

# write to spreadsheet
with open('spreadsheets/usernames.csv', 'wb') as f:
    writer = csv.writer(f)
    
    # Spreadsheet column headers:
    # - First column is the collected usernames
    # - Second column indicates whether a matching username on 
    # wikipedia and on twitter likely belongs to the same person
    all_columns = [USERNAME_COLUMN, MATCH_COLUMN]
    writer.writerow(all_columns)
    
    # write row for each user
    for username in users:
        user_row = []
        
        # first column is username
        user_row.append(username)
        
        # the username does exist on both wikipedia and twitter, but for now
        # we have not judged how likely the accounts belong to the same person.
        ''' TODO: Manually (using MTurk?) evaluate the likelihood that the
        wikipedia account and twitter account belong to the same person and
        update the spreadsheet accordingly. '''
        user_row.append(MATCH_UNKNOWN)
        
        writer.writerow(user_row)
