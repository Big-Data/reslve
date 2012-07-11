'''
Utility methods to access data through the Twitter API and parse results

Twitter account is required to use the API. Account details:
username: streamtest12345, pw: testinghere
consumer key: Bn62IlcOcgxKGYBTn17SGQ
consumer secret: H6TwsebK36zImYUTNbUc0QHzMmHd9NbaooVMgdiw

'''
import json
import pickle
import simplejson
import tweepy
import urllib
import urllib2
import webbrowser

# Given a list of usernames, performs batch lookups
# to Twitter API to fetch userinfo for those accounts
def batch_userlookup(all_screennames):
    print "Batch user lookup..."
    print all_screennames
    userlookups = []
    # users/lookup API takes up to 100 screennames, so may 
    # need to do multiple lookups depending on how large 
    # screennames list is
    start = 0
    end = min(start+100, len(all_screennames))
    while start < end:
        onehundred_users = all_screennames[start:end]
        onehundred_list = ','.join(onehundred_users)
        lookup_query = 'https://api.twitter.com/1/users/lookup.json?screen_name='+onehundred_list
        try :
            response = urllib2.urlopen(lookup_query).read()
            userlookups.extend(json.loads(response))
        except Exception as e:
            print "Unexpected exception while looking up user information. "
            print e
    
        start = start+100
        end = min(start+100, len(all_screennames))
        
    return userlookups

# Returns true if given user has a bio, false otherwise
def has_bio(user_info):
    try:
        description = user_info['description']
        if description!=None and description.strip()!='':
            return True
        else:
            return False
    except Exception as e:
        print "Bio of user caused error."
        print e
        return False

# Returns true if given user has made at least the
# given number of tweets, false otherwise
def has_enough_tweets(user_info, min_tweetcount):
    try:
        tweet_count = user_info['statuses_count']
        if tweet_count!=None and tweet_count>min_tweetcount:
            return True
        else:
            return False
    except:
        return False
    
# Uses the stream api to fetch tweets of the  
# twitter user accounts we have written to file
# http://api.twitter.com/1/statuses/user_timeline.json?screen_name=noradio&count=5
def fetch_tweets():

    print "Fetching tweets..."
    try:
        tweets_file = open('tweets.pkl', 'rb')
        tweets = pickle.load(tweets_file)
    except:
        tweets = {}
    
    api = __get_api__()
    
    twitter_users_file = open('twitter_accounts.pkl', 'rb')
    twitter_users = pickle.load(twitter_users_file)
    for twitter_user in twitter_users:
        screenname = twitter_user['screen_name']
        if screenname in tweets:
            # Already fetched tweets for that user
            continue
        user_tweets = []
        try:
            #print "Fetching tweets for user "+screenname+"..."
            tweepy_user_tweets = api.user_timeline(screenname, count=200)
            for tut in tweepy_user_tweets:
                try:
                    user_tweets.append(tut.text.encode("utf8"))
                except Exception as e1:
                    print "Problem with tweet "
                    print e1
        except Exception as e2:
            print "Exception while fetching tweets for user "+screenname
            print e2
            if 'Rate limit exceeded' in str(e2):
                break # don't keep querying once rate limit exceeded
        
        # Store a mapping from twitter username->tweets
        tweets[screenname] = user_tweets
    
    updated_tweets_file = open('tweets.pkl', 'wb')
    pickle.dump(tweets, updated_tweets_file)
    updated_tweets_file.close()

    print "Done fetching tweets."
    print "Current size of tweet store: "+str(len(tweets))

# Searches twitter using the given query and 
# returns an array of the resulting tweets
def search_for_tweets(query):
    search_host = 'http://search.twitter.com/'
    json_query_action = 'search.json?lang=en&rpp=100&q='
    xml_query_action = 'search.atom?lang=en&rpp=100&q='
    search_url = search_host+json_query_action
    
    query = urllib.quote(query)
    response = urllib2.urlopen(search_url+query).read()
    response = simplejson.loads(response.decode('utf-8'))
    search_results = response['results']
    return search_results 
    
# Provides authorizes access to the Twitter API
def __get_api__():
    consumer_key = 'Bn62IlcOcgxKGYBTn17SGQ'
    consumer_secret = 'H6TwsebK36zImYUTNbUc0QHzMmHd9NbaooVMgdiw'
    
    '''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    # Open authorization URL in browser
    webbrowser.open(auth.get_authorization_url())

    # Ask user for verifier pin
    pin = raw_input('Verification pin number from twitter.com: ').strip()

    # Get access token
    token = auth.get_access_token(verifier=pin)

    # Give user the access token
    print 'Access token:'
    print '  Key: %s' % token.key
    print '  Secret: %s' % token.secret
    '''
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token('555518563-4go92i8OBMTNI4uh4F4njF1GTQecY91GArJIhi9U', 'BypinoJNQEzNVK464rgsV2MwKaYhxYPuUdpo9nS3IV8')
    api = tweepy.API(auth)
    return api
