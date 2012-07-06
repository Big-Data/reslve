'''
Functions for querying wikipedia to get various 
pieces of information and for parsing results
'''
import datetime
import urllib2
import xml.dom.minidom

# number of most recently made edits to fetch for particular user:
num_useredits_tofetch = 50
min_editcount = 10

# Queries wikipedia to retrieve 
# various data in xml format
hosturl = 'http://en.wikipedia.org/'
queryaction = 'w/api.php?action=query&'
def query_wiki(query) : 
    result = urllib2.urlopen(hosturl+queryaction+query).read()
    return result

# Parses xml fetched from wikipedia to retrieve the 
# value of the given attribute within the given tag. 
def parse_wiki_xml(wiki_xml, tag_name, attribute) : 
    dom = xml.dom.minidom.parseString(wiki_xml)
    pages = dom.getElementsByTagName(tag_name)

    attr_list = []
    for page in pages : 
        if not page.hasAttribute(attribute):
            continue
        attr = page.getAttribute(attribute)
        if not attr in attr_list:
            attr_list.append(attr)
    return attr_list

def wiki_xml_has_tag(wiki_xml, tag_name):
    dom = xml.dom.minidom.parseString(wiki_xml)
    pages = dom.getElementsByTagName(tag_name)
    return len(pages) > 0

''' Fetch the given number of wikipedia editors who are 
active, ie have made a threshold number of non trivial edits. 
Returns a mapping from editor username->edited articles.'''
''' TODO this will not currently actually return n users?'''
def fetch_n_active_editors(n):
    
    editors = {}
    
    # want at least num unique editors, so will have to keep
    # requesting earlier changes until encounter that many editors
    start = datetime.datetime.now()
    end = start - datetime.timedelta(days=2)
    
    # fetch the most recently edited pages on wikipedia
    # until encounter n unique users who made those edits
    while len(editors) < n:
        
        recent_editors = query_recent_editors(start, end)
        print str(len(recent_editors))+" recent editors fetched"
        
        for username in recent_editors:
                
            # only consider editors that have edited at least a min number of pages
            try:
                if not is_active_user(username, num_useredits_tofetch):
                    continue
            except:
                continue

            # Get all of user's edits
            edited_pages =  query_user_edits(username)
            if len(edited_pages > min_editcount):
                editors[username] = edited_pages
            
            curr_len = len(editors)
            if curr_len%50==0:
                print str(curr_len)+" editors fetched so far.."
                
            ''' TODO '''
            start = start - datetime.timedelta(days=2)
            end = end - datetime.timedelta(days=2)
        
    print editors
    return editors

# Returns a mapping from page id -> number of times given user has edited that page
def query_user_edits(username):
    page_to_numedits = {}
    
    # only consider editors who have made non trivial edits
    ucshow = '&ucshow=!minor' # ignore minor edits
    # and for now, only include pages in default namespace 
    # to filter out edits like file uploads or user talk
    # see http://wiki.case.edu/api.php?action=query&meta=siteinfo&siprop=general|namespaces
    ucnamespace = '&ucnamespace=0'
    # ignore revert edits to fix vandalism, typo correction
    # uctag = ! 'rv' 
    '''TODO (rv flag in comment)??'''
    
    ucstart = ''
    while True:
        edits_query = 'list=usercontribs&ucuser='+username+'&uclimit=500'+ucnamespace+ucshow+'&format=xml'+ucstart
        user_edits_xml = query_wiki(edits_query)
        edited_pages = parse_wiki_xml(user_edits_xml, 'item', 'pageid')
        for page in edited_pages:
            if page in page_to_numedits.keys():
                numedits = page_to_numedits[page]
            else:
                numedits = 0
            page_to_numedits[page] = numedits+1
        
        query_continue = wiki_xml_has_tag(user_edits_xml, 'query-continue')  
        if not query_continue:
            break
        next_contribs = parse_wiki_xml(user_edits_xml, 'usercontribs', 'ucstart')
        ucstart = '&ucstart='+next_contribs[0]
    
    return page_to_numedits
    

''' Fetch the most recently edited pages on wikipedia between 
the given start and end dates and fetch the users who made those edits '''
def query_recent_editors(start_date, end_date):
    
    rclimit = '&rclimit=5000'
    
    # only list certain types of changes
    rctype = ('&rctype='
    +'edit'  # user responsible for the edit and tags if they are an IP
    +'|new') # page creations)
    
    # only show items that meet these criteria
    rcshow = ('&rcshow='
    +'!minor' # don't list minor edits
    +'|!bot' # don't list bot edits
    +'!anon') # only list edits by registered users
    
    # additional pieces of info to list:
    rcprop = ('&rcprop='
    +'user'  # user responsible for the edit and tags if they are an IP
    +'|userid' # user id responsible for the edit
    +'|flags' # flags for the edit
    +'|title' # page title of the edit
    +'|ids') # page ID, recent changes ID, and new and old revision ID
    
    # list newest changes first
    rcdir = ('&rcdir=older')
    
    # query wiki for recent edits
    params = rclimit+rctype+rcshow+rcprop+rcdir
    query = 'list=recentchanges'+params+'&format=xml'
    recent_edits = query_wiki(query)
    
    # get the users who made these edits
    editors = parse_wiki_xml(recent_edits, 'rc', 'user')
    return editors

# Return true if the given user has made at least 
# the given number of edits, false otherwise       
def is_active_user(user, min_editcount):
    editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
    editcount_xml = query_wiki(editcount_query)
    edit_count = parse_wiki_xml(editcount_xml, 'user', 'editcount')
    return (edit_count >= min_editcount)

'''
# From the given set of users, return a random user
# who has made at least the given number of edits
def get_random_active_user(users, min_editcount):
    for user in users:
        editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
        editcount_xml = query_wiki(editcount_query)
        edit_count = parse_wiki_xml(editcount_xml, 'user', 'editcount')
        if edit_count >= 50: 
            return user
'''

# Returns the wikipedia categories of a wikipedia resource given its id
def fetch_categories(res_id):
    categories_query = 'pageids='+str(res_id)+'&prop=categories&clshow=!hidden&format=xml'
    categories_xml = query_wiki(categories_query)
    categories = parse_wiki_xml(categories_xml, 'cl', 'title')
    formatted_categories = []
    for cat in categories:
        formatted_categories.append(__format_category__(cat))
    return formatted_categories

''' Formats the category string:
- a. remove "Category:" namespace
- b. make lowercase
- c. remove leading and trailing white space
'''
def __format_category__(category):
    category = category.replace("Category:", "") #a
    category = category.lower() #b
    category = category.strip() #c
    return category
