'''
Functions to query wikipedia for various 
pieces of information and to parse results
'''
import urllib2
import xml.dom.minidom

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
        user_edits_xml = __query_wiki__(edits_query)
        edited_pages = __parse_wiki_xml__(user_edits_xml, 'item', 'pageid')
        for page in edited_pages:
            if page in page_to_numedits.keys():
                numedits = page_to_numedits[page]
            else:
                numedits = 0
            page_to_numedits[page] = numedits+1
        
        query_continue = __wiki_xml_has_tag__(user_edits_xml, 'query-continue')  
        if not query_continue:
            break
        next_contribs = __parse_wiki_xml__(user_edits_xml, 'usercontribs', 'ucstart')
        ucstart = '&ucstart='+next_contribs[0]
    
    return page_to_numedits

# Return true if the given user has made at least 
# the given number of edits, false otherwise       
def is_active_user(user, min_editcount):
    editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
    editcount_xml = __query_wiki__(editcount_query)
    edit_count = __parse_wiki_xml__(editcount_xml, 'user', 'editcount')
    return (edit_count >= min_editcount)

''' Fetch the most recently edited pages on 
wikipedia and the users who made those edits '''
def query_recent_editors():
    
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
    recent_edits = __query_wiki__(query)
    
    # get the users who made these edits
    editors = __parse_wiki_xml__(recent_edits, 'rc', 'user')
    return editors

# From the given set of users, return a random user
# who has made at least the given number of edits
def get_random_active_user(users, min_editcount):
    for user in users:
        editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
        editcount_xml = __query_wiki__(editcount_query)
        edit_count = __parse_wiki_xml__(editcount_xml, 'user', 'editcount')
        if edit_count >= min_editcount: 
            return user

# Returns the wikipedia categories of a wikipedia resource given its id
def query_categories(res_id):
    categories_query = 'pageids='+str(res_id)+'&prop=categories&clshow=!hidden&format=xml'
    categories_xml = __query_wiki__(categories_query)
    categories = __parse_wiki_xml__(categories_xml, 'cl', 'title')
    formatted_categories = []
    for cat in categories:
        formatted_categories.append(__format_category__(cat))
    return formatted_categories

# Queries wikipedia to retrieve 
# various data in xml format
hosturl = 'http://en.wikipedia.org/'
queryaction = 'w/api.php?action=query&'
def __query_wiki__(query) : 
    result = urllib2.urlopen(hosturl+queryaction+query).read()
    return result

# Parses xml fetched from wikipedia to retrieve the 
# value of the given attribute within the given tag. 
def __parse_wiki_xml__(wiki_xml, tag_name, attribute) : 
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

def __wiki_xml_has_tag__(wiki_xml, tag_name):
    dom = xml.dom.minidom.parseString(wiki_xml)
    pages = dom.getElementsByTagName(tag_name)
    return len(pages) > 0

''' Formats the category string in the following ways:
    1. remove leading and trailing white space
'''
def __format_category__(category):
    category = category.strip()
    return category
