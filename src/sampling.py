'''
Finds a sample of users that are both wikipedia editors and twitter 
users. Writes their edited articles and tweets to file.
'''
import User_Categories
import account_matching
import named_entity_finder
import pickle
import pprint
import string
import twitter_util
import wiki_fetch_util

def fetch_wiki_editors():
    # fetch 1500 active wiki editors
    print "Fetching wikipedia editors..."
    editors = wiki_fetch_util.fetch_n_active_editors(1500) 
    
    # write to file
    editors_file = open('sample_dump/editors.pkl', 'wb')
    pickle.dump(editors, editors_file)
    editors_file.close()
    print "Retrieved "+str(len(editors))+" active wikipedia editors"
    
def fetch_matching_tweeters():
    print "Matching wikipedia editors to twitter accounts..."
    # load active wiki editors
    editors_file = open('sample_dump/editors.pkl', 'rb')
    editors = pickle.load(editors_file)
    
    # find twitter accounts belonging to the same users
    usernames = editors.keys()
    twitter_accounts = account_matching.find_twitter_matches(usernames, 1)
    print "Found "+str(len(twitter_accounts))+" matching twitter accounts"
    
    # write to file
    twitter_accounts_file = open('sample_dump/twitter_accounts.pkl', 'wb')
    pickle.dump(twitter_accounts, twitter_accounts_file)
    twitter_accounts_file.close()
    
def fetch_tweet_named_entities():
    print "Detecting surface forms in tweets and identifying candidate resources..."
    tweets_file = open('sample_dump/tweets.pkl', 'rb')
    tweets = pickle.load(tweets_file)
    tweet_candidates = {}
    #count = 0
    for user in tweets:
        #if count > 10: 
        #    break
        user_tweets = tweets[user]
        for tweet in user_tweets:
            print "tweet! "+tweet
            try:
                named_entities = named_entity_finder.find_named_entities(tweet)
                pprint.pprint(named_entities)
                surface_forms = named_entities['annotation']['surfaceForm']
                tweet_candidates[tweet] = surface_forms
            except:
                continue
        #count = count + 1
        
    # write to file
    tweet_candidates_file = open('sample_dump/tweet_candidates.pkl', 'wb')
    pickle.dump(tweet_candidates, tweet_candidates_file)
    tweet_candidates_file.close()
    

def get_user_mapping(filename):
    userfile = open(filename, 'rb')
    mapping = pickle.load(userfile)
    # username may be capitalized for one account and not other, so ignore case
    mapping = dict(zip(map(string.lower,mapping.keys()),mapping.values()))
    return mapping
def get_editors_mapping():
    return get_user_mapping('sample_dump/editors.pkl')
def get_twitter_accounts_mapping():
    return get_user_mapping('sample_dump/tweets.pkl')
    
def build_user_models():
    print "Creating user's category mapping based on wikipedia edits..."
    # load users with active wiki + twitter accounts
    editors = get_editors_mapping()
    twitter_users = get_twitter_accounts_mapping()
    user_models = {}
    for username in twitter_users.keys():
        # get the categories of user's edited pages and put them in a mapping 
        # from category -> number of edits made to pages with that category
        edited_pages = editors[username]
        user_interests = User_Categories.User_Categories(username)
        for edited_page_id in edited_pages:
            categories = wiki_fetch_util.fetch_categories_of_id(edited_page_id)
            user_interests.add_categories(categories)
        user_models[username] = user_interests
        
    # write to file
    interests_file = open('sample_dump/interests_models.pkl', 'wb')
    pickle.dump(user_models, interests_file)
    interests_file.close()
    
# fetch wiki editors
#fetch_wiki_editors()

# then fetch matching twitter accounts
#fetch_matching_tweeters()

# fetch the tweets of those twitter accounts
# twitter_util.fetch_tweets()

# fetch named entities of those tweets
#fetch_tweet_named_entities()

# build user interest model for those users, which we will use
# to find candidate resources for ambiguous entities in the tweets
#build_user_models()
