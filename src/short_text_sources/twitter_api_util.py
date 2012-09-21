# -*- coding: utf-8 -*-
'''
Utility methods to access data through the Twitter API and parse results.

Twitter account is required to use the API. Account details:
username: streamtest12345, pw: testinghere
consumer key: Bn62IlcOcgxKGYBTn17SGQ
consumer secret: H6TwsebK36zImYUTNbUc0QHzMmHd9NbaooVMgdiw

'''
from CONSTANT_VARIABLES import ACTIVE_TWITTER_MIN
import json
import oauth2 as oauth
import pickle
import simplejson
import tweepy
import urllib
import urllib2
#import unicodedata
#import webbrowser


###### Methods for working with the Twitter API ######

def userlookup(all_screennames, num_lookups_desired, existing_key, nonexisting_key, rate_limit_key):
    ''' Given a list of usernames, performs batch lookups to Twitter API
    to fetch extended user info for those accounts. Maps usernames to indicate 
    whether they do or do not exist on Twitter. Also includes a key-value 
    pair to indicate whether or not the rate limit has been reached, ie
    { exist : [userinfo, userinfo, ...]
      don't exist : [username, username, ...]
      rate limit reached: True or False } '''
    print 'Looking up '+str(len(all_screennames))+' usernames on Twitter...'
    
    existing_userinfos = []
    nonexisting_usernames = []
    rate_limit_reached = False
    userlookups = {existing_key:existing_userinfos, nonexisting_key:nonexisting_usernames, 
                   rate_limit_key:rate_limit_reached}
    
    # authenticate so we can make more requests to Twitter API
    client = __get_client__()
    
    # users/lookup API takes up to 100 screennames, so may 
    # need to do multiple lookups depending on how large 
    # screennames list is
    start = 0
    end = min(start+100, len(all_screennames))
    progress_count = 1
    while start < end:
        
        if len(existing_userinfos) >= num_lookups_desired:
            # if fetched desired number of usernames, no need 
            # to keep querying twitter until hit rate limit
            break  
        
        if progress_count%50==0:
            print "Querying to test whether usernames exist or don't exist on Twitter... "+\
            "Number usernames analyzed so far: "+str(progress_count)
        progress_count = progress_count+1
        
        onehundred_users = all_screennames[start:end]
        onehundred_list = ','.join(onehundred_users)
        lookup_query = 'https://api.twitter.com/1/users/lookup.json?screen_name='+onehundred_list
        try :
            response, content = client.request(lookup_query, 'GET')
            existing_userinfos.extend(json.loads(content)) # these usernames exist
        except Exception as e:
            if 'HTTP Error 400: Bad Request' in str(e):
                # This is the status code returned during rate limiting.
                # https://dev.twitter.com/docs/error-codes-responses
                #print "Twitter rate limit reached when looking up extended user infos. Exiting."
                rate_limit_reached = True
                break

        start = start+100
        end = min(start+100, len(all_screennames))
        
        # remove any usernames that we already determined do not exist on given site
        existing_usernames = [eui['screen_name'].lower() for eui in existing_userinfos]
        usernames_with_no_userinfo = [u for u in onehundred_users if u not in existing_usernames]
        nonexisting_usernames.extend(usernames_with_no_userinfo)
        
    userlookups[rate_limit_key] = rate_limit_reached
    return userlookups

def fetch_user_tweets_Tweepy(api, screenname, tweets_key, rate_limit_key, num_tweets_to_fetch=ACTIVE_TWITTER_MIN, fetch_full_tweet_obj=False):
    user_tweets = []
    rate_limit_reached = False
    try:
        #print "Fetching tweets for user "+screenname+"..."
        tweepy_user_tweets = api.user_timeline(screenname, count=num_tweets_to_fetch)
        for tut in tweepy_user_tweets:
            try:
                if fetch_full_tweet_obj:
                    user_tweets.append(tut)
                else:
                    # just return the tweet text if tweet object not requested
                    user_tweets.append(tut.text.replace('\r', ' ').encode('utf-8'))
            except Exception as e1:
                print "Problem with tweet "
                print e1
    except Exception as e2:
        if 'Rate limit exceeded' in str(e2):
            print "Twitter rate limit reached when querying twitter for tweets. Exiting."
            rate_limit_reached = True
        
    tweets_response = {}
    tweets_response[tweets_key] = user_tweets
    tweets_response[rate_limit_key] = rate_limit_reached
    return tweets_response

def fetch_tweets_StreamAPI():
    ''' 'Uses the stream api to fetch tweets of the 
    twitter user accounts we have written to file 
    http://api.twitter.com/1/statuses/user_timeline.json?screen_name=noradio&count=5 '''

    print "Fetching tweets..."
    try:
        tweets_file = open('tweets.pkl', 'rb')
        tweets = pickle.load(tweets_file)
    except:
        tweets = {}
    
    api = __get_api_for_tweepy__()
    
    twitter_users_file = open('twitter_accounts.pkl', 'rb')
    twitter_users = pickle.load(twitter_users_file)
    for twitter_user in twitter_users:
        screenname = twitter_user['screen_name']
        if screenname in tweets:
            # Already fetched tweets for that user
            continue
        user_tweets = fetch_user_tweets_Tweepy(api, screenname, 200)
        
        # Store a mapping from twitter username->tweets
        tweets[screenname] = user_tweets
    
    updated_tweets_file = open('tweets.pkl', 'wb')
    pickle.dump(tweets, updated_tweets_file)
    updated_tweets_file.close()

    print "Done fetching tweets."
    print "Current size of tweet store: "+str(len(tweets))

def fetch_tweets_SearchAPI(query):
    ''' Searches twitter using the given query and 
    returns an array of the resulting tweets '''
    search_host = 'http://search.twitter.com/'
    json_query_action = 'search.json?lang=en&rpp=100&q='
    #xml_query_action = 'search.atom?lang=en&rpp=100&q='
    search_url = search_host+json_query_action
    
    query = urllib.quote(query)
    response = urllib2.urlopen(search_url+query).read()
    response = simplejson.loads(response.decode('utf-8'))
    search_results = response['results']
    return search_results 


###### Methods for parsing data retrieved via the Twitter API ######

def has_enough_tweets(user_info, min_tweetcount):
    ''' Returns true if given user has made at least  
    the given number of tweets, false otherwise '''
    try:
        tweet_count = user_info['statuses_count']
        if tweet_count!=None and tweet_count>min_tweetcount:
            return True
        else:
            return False
    except:
        return False
    
def has_bio(user_info):
    ''' Returns true if given user has a bio, false otherwise '''
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


########## Authentication handling so we can make more requests to Twitter API:

__consumer_key__ = 'Bn62IlcOcgxKGYBTn17SGQ'
__consumer_secret__ = 'H6TwsebK36zImYUTNbUc0QHzMmHd9NbaooVMgdiw'
__access_key__ = '555518563-4go92i8OBMTNI4uh4F4njF1GTQecY91GArJIhi9U'
__access_secret__ = 'BypinoJNQEzNVK464rgsV2MwKaYhxYPuUdpo9nS3IV8'
def __get_client__():
    consumer = oauth.Consumer(__consumer_key__, __consumer_secret__)
    token = oauth.Token(key=__access_key__, secret=__access_secret__)
    client = oauth.Client(consumer, token)
    return client
def __get_api_for_tweepy__():
    ''' Provides authorizes access to the Twitter API '''
    
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
    
    auth = tweepy.OAuthHandler(__consumer_key__, __consumer_secret__)
    auth.set_access_token(__access_key__, __access_secret__)
    api = tweepy.API(auth)
    return api