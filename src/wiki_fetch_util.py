'''
Functions for querying wikipedia to get various 
pieces of information and for parsing results
'''
import urllib2
import xml.dom.minidom

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
        attr = page.getAttribute(attribute)
        if not attr in attr_list:
            attr_list.append(attr)
    return attr_list

''' Fetch the most recently edited pages on wikipedia until 
encounter the given num of unique users who made those edits '''
def query_n_most_recent_editors(num):
    
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
    params = str(num)+rctype+rcshow+rcprop+rcdir
    query = 'list=recentchanges&rclimit='+params+'&format=xml'
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