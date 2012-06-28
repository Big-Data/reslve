import User_Categories
import named_entity_finder
import pickle
import score_util
import wiki_fetch_util

'''
# look for some usernames that have tweets we can disambiguate..
usernames_file = open('sample_dump/twitter_accounts.pkl', 'rb')
usernames = pickle.load(usernames_file)
print usernames
for u in usernames:
    print u['screen_name']
    print u['statuses_count']
'''
'''    
jmj713
**  Roth sold out, five days after publication. Back to press for a second
    King gives new history lessons
    Do we really need another Holmes?
    Burgess archive reveals vast body of previously unseen work
    In Winter Classic, Rangers Nip Flyers, Al Fresco
    Ward awarded a goal. Meh. How about joining the rush and scoring?
    Bush is the least popular living president - apparently absence does not make the heart
LisaMLane
    I love the Queen too, @edwebb forgive me - I know royalty are wasteful and non-democratic. I confess I like Charles too.
Torchiest 
    Perry talks like he's downloading his words through a bad wifi connection.
    How does the future of the Tea Party intersect with the future of libertarianism? Can they make a new third party?
hamish59
jasonwells1982
godofredo29
Nicokroeker    
dmacks
bpositive
christofhe
Bjahnke
jbraith
cgiese
katmaan
sss28
buaidh
TheLeftorium
ghosttownaz
Leisurist
AgentSniff
barbthebuilder
SnowmanRadio
DJLN
mimich
arjann
JohnArmagh
Ricjac
musdan77
DrKiernan
barbaracarder
JoeSperrazza
oceanflynn
DMcQ
illazilla
'''

# user -> interests (categories)
username = raw_input("Enter username: ")
interests_file = open('sample_dump/interests_models.pkl', 'rb')
user_models = pickle.load(interests_file)
if user_models.has_key(username):
    user_interests = user_models[username]
else:
    edits_query = 'list=usercontribs&ucuser='+username+'&uclimit=100&ucnamespace=0&ucshow=!minor&format=xml'
    user_edits_xml = wiki_fetch_util.query_wiki(edits_query)
    edited_pages = wiki_fetch_util.parse_wiki_xml(user_edits_xml, 'item', 'pageid')
    user_interests = User_Categories.User_Categories(username)
    for edited_page_id in edited_pages:
        categories = wiki_fetch_util.fetch_categories_of_id(edited_page_id)
        user_interests.add_categories(categories)
user_categories_map = user_interests.get_categories()
user_categories = user_categories_map.keys()
print user_categories

tweets_file = open('sample_dump/tweets.pkl', 'rb')
tweets = pickle.load(tweets_file)
if tweets.has_key(username):
    user_tweets = tweets[username]
    print user_tweets

# tweet -> detect entities -> for ambiguous entities, get candidates -> score candidate categories against user categories
tweet = raw_input("Enter tweet: ")
entities_map = named_entity_finder.find_ambiguous_named_entities_wikipedia_miner(tweet)
for surface_form in entities_map.keys():
    print "Ambiguous term: "+surface_form
    try:
        candidates = entities_map[surface_form]
        count = 1
        for candidate in candidates:
            try:
                article_id = candidate['article_id']
                title = candidate['title']
                dbpedia_uri = candidate['dbpedia_uri']
                print "Candidate "+str(count)+" of "+str(len(candidates))+": "+title
                count = count+1
                
                # wikiminer disambiguation
                weight = candidate['weight']
                print "Rank according to Wikipedia Miner: "+str(weight)

                # our disambiguation
                candidate_categories = wiki_fetch_util.fetch_categories_of_id(article_id)
                ''' TODO switch this to use the full category hierarchy '''
                jacc_sim = score_util.jaccard_similarity(candidate_categories, user_categories)
                print "Rank according to us: "+str(jacc_sim)
                
            except Exception as e1:
                print e1
                continue
    except Exception as e2:
        print e2
        continue
