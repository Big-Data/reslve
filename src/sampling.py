'''
Finds a sample of users that are both wikipedia editors and twitter 
users. Writes their edited articles and tweets to file.
'''
from good import matching
import pickle
import twitter_util
import wiki_fetch_util

def fetch_wiki_editors():
    # fetch 1500 active wiki editors
    print "Fetching wikipedia editors..."
    editors = wiki_fetch_util.fetch_n_active_editors(1500) 
    
    # write to file
    editors_file = open('editors.pkl', 'wb')
    pickle.dump(editors, editors_file)
    editors_file.close()
    print "Retrieved "+str(len(editors))+" active wikipedia editors"
    
def fetch_matching_tweeters():
    print "Matching wikipedia editors to twitter accounts..."
    # load active wiki editors
    editors_file = open('editors.pkl', 'rb')
    editors = pickle.load(editors_file)
    
    # find twitter accounts belonging to the same users
    usernames = editors.keys()
    twitter_accounts = matching.find_twitter_matches(usernames, 1)
    print "Found "+str(len(twitter_accounts))+" matching twitter accounts"
    
    # write to file
    twitter_accounts_file = open('twitter_accounts.pkl', 'wb')
    pickle.dump(twitter_accounts, twitter_accounts_file)
    twitter_accounts_file.close()
    
# fetch wiki editors
#fetch_wiki_editors()

# then fetch matching twitter accounts
#fetch_matching_tweeters()

# fetch the tweets of those twitter accounts
twitter_util.fetch_tweets()
