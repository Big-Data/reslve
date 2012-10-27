""" The websites from which we obtain users and short texts """
from CONSTANT_VARIABLES import ACTIVE_TWITTER_MIN
from short_text_sources import twitter_api_util

__Twitter_SiteName__ = 'Twitter'
def get_twitter_site():
    return Twitter_Site(__Twitter_SiteName__)
def site_is_Twitter(site):
    return site!=None and site.siteName==__Twitter_SiteName__


####### The site "Interface" #######
class Site(object):
    ''' Represents a website from which we draw short texts '''
    def __init__(self, siteName):
        ''' @param siteName: The website, should be one of the SITE_* variables in VARS.py '''
        self.siteName = siteName
    def fetching_existence_status(self):
        print "Fetching existing "+str(self.siteName)+" accounts..."
        
####### Twitter #######        
class Twitter_Site(Site):
    ''' Represents the website Twitter, from which we draw tweets as short texts '''
    
    def __init__(self, siteName):
        '''  @param siteName: The website, should be one of the SITE_* variables in VARS.py '''
        Site.__init__(self, siteName)
        
    def fetching_existence_status(self, usernames, desired_num_usernames):
        ''' Returns a map of the usernames that exist and meet the minimum 
        contribution requirement, the usernames that do not exist or do not meet
        the minimum contributino requirement, and the rate limit status, ie
        { exist and active : [username, username, ...]
          don't exist or not active : [username, username, ...]
          rate limit reached : True or False }
        
        @param usernames: The usernames on which to search for Twitter accounts
        @param min_num_texts:  The minimum number of tweets the Twitter account
        must have written in order to be considered a valid matching account
        '''
        Site.fetching_existence_status(self) # just prints a message to console

        # lookup extended user info
        existing_key = self.get_existing_response_key()
        nonexisting_key = self.get_nonexisting_response_key()
        rate_limit_key = self.get_rate_limit_key()
        lookups = twitter_api_util.userlookup(usernames, desired_num_usernames, 
                                              existing_key, nonexisting_key, rate_limit_key)
        
        # extended user info for accounts that exist on Twitter
        existing_userinfos = lookups[existing_key]
        # usernames of accounts that do not exist on Twitter
        nonexisting_usernames = lookups[nonexisting_key]
        
        # filter out those with enough tweets
        existing_and_active = []
        for account in existing_userinfos:
            try:
                num_tweets = account['statuses_count']
                account_name = account['screen_name'].lower()
                
                # if active, add to the existing and active list, 
                # otherwise add to the other list that indicates
                # a username is nonexistent or nonactive
                if num_tweets >= ACTIVE_TWITTER_MIN:
                    existing_and_active.append(account_name)
                else: 
                    # otherwise, move out of the existing + active
                    # list and into the nonexisting + nonactive list
                    nonexisting_usernames.append(account_name)
            except:
                # just ignore this username if its problematic
                nonexisting_usernames.append(account_name)
                continue 
            
        match_response = {existing_key:existing_and_active, 
                          nonexisting_key:nonexisting_usernames, 
                          rate_limit_key:lookups[rate_limit_key]}
        return match_response
    
    def likehood_same_person(self, username):
        ''' Calculates and returns the likelihood that the given username that 
        exists on both wikipedia and twitter actually belongs to the same person.
        
        The value returned is based on the following attributes matching:
        - Location
        - Email
        - Real name
        A matching attribute contributes +1, a mismatched attribute contributes -1, 
        and the value of the attribute missing for either the wikipedia, twitter, 
        or both accounts contributes 0
        '''
        ''' TODO '''
        return 0
    
    def get_existing_response_key(self):
        return 'EXISTING_USERNAMES_KEY_'+str(self.siteName)
    
    def get_nonexisting_response_key(self):
        return 'NONEXISTING_USERNAMES_KEY_'+str(self.siteName)
    
    def get_shorttext_response_key(self):
        return 'SHORTTEXT_RESPONSE_KEY_'+str(self.siteName)

    def get_rate_limit_key(self):
        ''' Returns the key that maps to whether or not rate 
        limit has been reached while querying this site. '''
        return 'RATE_LIMIT_KEY_'+str(self.siteName)
    
    def get_user_short_texts(self, username):
        ''' Fetches the given number of tweets posted by the given 
        username and returns a mapping of tweet id -> tweet text wrapped
        in a mapping that indicates whether the rate limit has been reached '''
        
        api = twitter_api_util.__get_api_for_tweepy__()
        tweets_key = 'tweets_key'
        rate_limit_key = self.get_rate_limit_key()
        
        tweets_response = twitter_api_util.fetch_user_tweets_Tweepy(api, username, 
                                                                    tweets_key, rate_limit_key, 
                                                                    fetch_full_tweet_obj=True)
        user_tweets = tweets_response[tweets_key]
        
        tweet_mapping = {}
        for tweepy_user_tweet in user_tweets:
            tweet_mapping[tweepy_user_tweet.id] = tweepy_user_tweet.text.replace('\r', ' ').encode('utf-8')
            
        shorttext_response = {}
        shorttext_response[self.get_shorttext_response_key()] = tweet_mapping
        shorttext_response[rate_limit_key] = tweets_response[rate_limit_key]
        return shorttext_response
