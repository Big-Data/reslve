''' Functions relating to finding accounts 
that correspond to the same individual '''

import twitter_util

# Returns objects corresponding to the twitter accounts
# that match the given usernames, if they exist. Also, filtering
# out twitter accounts that have tweeted less than the given minimum
# number of tweets.
def find_twitter_matches(usernames, min_tweets):
    print "Looking up Twitter accounts..."
    userinfos = twitter_util.batch_userlookup(usernames)
    return userinfos
    
# Calculates and returns the probability that the
# given wikipedia editor and the given twitter account
# belong to the same person.
def probability_same(wikipedia_user, twitter_user):
    print "calculating prob"
