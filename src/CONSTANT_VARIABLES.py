####### GLOBAL CONSTANT VARIABLES #######

DEBUG_ON = False

''' Spreadsheet column strings that will be used to 
identify the same information in multiple spreadsheets: '''

COLUMN_USERNAME = 'username'

COLUMN_SHORTTEXT_ID = "shorttextID"
COLUMN_SHORTTEXT_STRING =  "shorttextString"




''' Requirements to be considered an "active" user, ie minimum 
number of contributions on wikipedia/twitter/flickr/etc: '''

# Hauff: "Placing Images on the World Map": 10 on Twitter, 5 on Flickr
ACTIVE_WIKIPEDIA_MIN = 100 

# maximum number of pages most recently edited by a user on 
# Wikipedia that we'll consider; any more will result in an
# interest model that is too diverse and noisy?
# ACTIVE_WIKIPEDIA_MAX = 100

# Zhang, "Community Discovery in Twitter Based on User Interests": 100=active
# Lu, Lam, Zhang: "Twitter User Modeling...": 100=active
# Naaman, "Is it really about me": 10=active
# Counts, Fisher: "Taking It All In?": 10=active
ACTIVE_TWITTER_MIN = 100 