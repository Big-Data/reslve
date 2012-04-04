'''
Collecting edited wikipedia pages and the categories
they belong to so we can model users' domain knowledge. 
'''
from User_Interests import User_Interests
import csv
import wiki_fetch_util

# number of most recently made edits on wikipedia by anyone:
num_wikiedits_tofetch = 500
# number of most recently made edits to fetch for particular user:
num_useredits_tofetch = 50

# ============================================================================
# Functions:

# Write the data to a spreadsheet where each row corresponds
# to a different user and there is a column for every category 
# that any of those users has edited a page from.   
def write_csv(all_categories, user_models):
    with open('user_categories.csv', 'wb') as f:
        writer = csv.writer(f)
        
        # write column headers
        # column headers: userid category0 category1 ... categoryN
        all_columns = []
        all_columns.append('userid')
        all_columns.extend(all_categories)
        writer.writerow(all_columns)
    
        # write row for each user
        for user_model in user_models:
            user_row = []
        
            # first column is user id
            user_id = user_model.get_userid()   
            user_row.append(user_id)
        
            # column for each category any of user made edit(s) in
            user_categories = user_model.get_categories()
            for category in all_categories:
                # value in a cell is number of pages user edited that belong to 
                # that category or 0 if user has edited no pages from that category
                if user_categories.has_key(category):
                    num = user_categories[category]
                else: 
                    num = 0
                user_row.append(num)
            
            writer.writerow(user_row)
    
# ============================================================================


print "Fetching data..."
    
# fetch the most recently edited pages on wikipedia
# until encounter i unique users who made those edits
users = wiki_fetch_util.query_n_most_recent_editors(num_wikiedits_tofetch)

# filtering out certain edit patterns:
# want non-minor edits
ucshow = '&ucshow=!minor' 
# for now, only include pages in default namespace 
# to filter out edits like file uploads or user talk
# see http://wiki.case.edu/api.php?action=query&meta=siteinfo&siprop=general|namespaces
ucnamespace = '&ucnamespace=0'
# revert edits to fix vandalism, typo correction
# uctag = ! 'rv' TODO (rv flag in comment)

user_models = []
users = []
for user in users:
    
    # only consider users that have edited at least a min number of pages
    try:
        if not wiki_fetch_util.is_active_user(user, num_useredits_tofetch):
            continue
    except:
        continue
    
    # For each user, get his last j edited articles.
    # Note this is different than last j edits because we consider
    # multiple edits of the same article as a single contribution, 
    # so the latter number could be bigger than the former. 
    edits_query = 'list=usercontribs&ucuser='+user+'&uclimit='+str(num_useredits_tofetch)+ucnamespace+ucshow+'&format=xml'
    user_edits_xml = wiki_fetch_util.query_wiki(edits_query)
    edited_pages = wiki_fetch_util.parse_wiki_xml(user_edits_xml, 'item', 'pageid')
    
    # get the categories of those edited pages and put them in a mapping 
    # from category -> number of edits made to pages with that category
    user_interests = User_Interests(user)
    for edited_page_id in edited_pages:
        categories_query = 'pageids='+edited_page_id+'&prop=categories&format=xml'
        categories_xml = wiki_fetch_util.query_wiki(categories_query)
        categories = wiki_fetch_util.parse_wiki_xml(categories_xml, 'cl', 'title')
        user_interests.add_categories(categories)
            
    user_models.append(user_interests)
    
print "Writing data to csv file..."

# get all categories from which any of the users has edited a page
all_categories = []
for user_model in user_models:
    categories_to_numedits = user_model.get_categories()
    categories = categories_to_numedits.keys()
    print categories_to_numedits
    for cat in categories:
        if not cat in all_categories:
            all_categories.append(cat)
            
# write to csv
write_csv(all_categories, user_models)

print "Done"
