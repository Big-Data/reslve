####### GLOBAL CONSTANT VARIABLES #######

DEBUG_ON = False

''' Spreadsheet column strings that will be used to 
identify the same information in multiple spreadsheets: '''

COLUMN_USERNAME = 'username'

COLUMN_SHORTTEXT_ID = "shorttextID"
COLUMN_SHORTTEXT_STRING =  "shorttextString"

COLUMN_ENTITY_ID = "entityID"


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

''' The identifiers for the various strategies we use to disambiguate
an entity (Turker judgements, toolkit services, RESLVE ranking functions): '''

GOLD_MechanicalTurker = 'mechanical_turk_judgement'

BASELINE_WikipediaMiner = 'wikipedia_miner_algorithm'
BASELINE_DbpediaSpotlight = 'dbpedia_spotlight_algorithm'

RESLVE_ArticleContentBowVsm = 'article_contentbow_vsm_algorithm'
RESLVE_ArticleIdVsm = 'article_id_vsm_algorithm'
RESLVE_ArticleTitleBowVsm = 'article_titlebow_vsm_algorithm'

RESLVE_DirectCategoryIdVsm = 'directcategory_id_vsm_algorithm'
RESLVE_DirectCategoryTitleBowVsm = 'directcategory_titlebow_vsm_algorithm'

RESLVE_GraphCategoryIdVsm = 'graphcategory_id_vsm_algorithm'
RESLVE_GraphCategoryTitleBowVsm = 'graphcategory_titlebow_vsm_algorithm'

RESLVE_ArticleContentBow_Wsd = 'article_contentbow_wsd_algorithm'


# Entity types we restrict our sample to. (See http://schema.org/Thing)
VALID_RDF_TYPES = ['http://schema.org/CreativeWork',
                   'http://schema.org/Event',
                   #'http://schema.org/Intangible',
                   'http://schema.org/MedicalEntity',
                   'http://schema.org/Organization',
                   'http://schema.org/Person',
                   'http://schema.org/Place',
                   'http://schema.org/Product']