''' Functions relating to finding accounts 
that correspond to the same individual '''

import twitter_util

# Returns objects corresponding to the twitter accounts, if 
# they exist, that have the given usernames. Does not return
# twitter accounts that have tweeted less than the given minimum
# number of tweets.
def find_twitter_matches(usernames, min_tweets):
    print "Looking up Twitter accounts..."
    # lookup..
    userinfos = twitter_util.batch_userlookup(usernames)
    # filter out..
    matches = []
    for account in userinfos:
        try:
            num_tweets = account['statuses_count']
            if num_tweets >= min_tweets:
                matches.append(account['screen_name'])
        except:
            continue
    return matches
    
# Calculates and returns the probability that the
# given wikipedia editor and the given twitter account
# belong to the same person.
''' TODO '''
def probability_same(wikipedia_user, twitter_user):
    print "calculating prob"
    

