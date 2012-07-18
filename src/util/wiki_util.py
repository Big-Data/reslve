'''
Functions to query wikipedia for various 
pieces of information and to parse results
'''
import urllib2
import xml.dom.minidom

def query_user_edits(username):
    '''Returns a mapping from page id -> number of times given user has edited that page'''
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
            try:
                if page in page_to_numedits.keys():
                    numedits = page_to_numedits[page]
                else:
                    numedits = 0
                page_to_numedits[page] = numedits+1
            except:
                continue
        
        query_continue = __wiki_xml_has_tag__(user_edits_xml, 'query-continue')  
        if not query_continue:
            break
        next_contribs = __parse_wiki_xml__(user_edits_xml, 'usercontribs', 'ucstart')
        ucstart = '&ucstart='+next_contribs[0]
    
    return page_to_numedits

def query_page_edits(page_id):
    ''' Returns the total number of revisions ever made on the given page by anyone '''
    total_num_edits = 0
    rvstart = ''
    while True:
        edits_query = 'prop=revisions&pageids='+str(page_id)+'&rvlimit=5000&format=xml'+str(rvstart)
        edits_xml = __query_wiki__(edits_query)
        edited_pages = __parse_wiki_xml__(edits_xml, 'rev', 'revid')
        total_num_edits = total_num_edits + len(edited_pages)
        
        query_continue = __wiki_xml_has_tag__(edits_xml, 'query-continue')  
        if not query_continue:
            break
        next_revisions = __parse_wiki_xml__(edits_xml, 'revisions', 'rvstartid')
        rvstart = '&rvstartid='+next_revisions[0]
    
    return total_num_edits

def query_hierarchy_edits(category_hierarchy):
    ''' Returns the total number of revisions ever made on the source article of the given Category_Hierarchy '''
    return query_page_edits(category_hierarchy.get_source_article_id())

def query_total_edits():
    ''' Returns the total number of edits made on Wikipedia '''
    stats_query = 'meta=siteinfo&siprop=statistics&format=xml'
    stats_xml = __query_wiki__(stats_query)
    edit_stat = __parse_wiki_xml__(stats_xml, 'statistics', 'edits')
    return edit_stat

def is_active_user(user, min_editcount):
    ''' Return true if the given user has made at least 
    the given number of edits, false otherwise  '''
    editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
    editcount_xml = __query_wiki__(editcount_query)
    edit_count = __parse_wiki_xml__(editcount_xml, 'user', 'editcount')
    return (edit_count >= min_editcount)

def query_recent_editors():
    ''' Fetch the most recently edited pages on 
    wikipedia and the users who made those edits '''
    
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

def get_random_active_user(users, min_editcount):
    ''' From the given set of users, return a random user 
    who has made at least the given number of edits '''
    for user in users:
        editcount_query = 'list=users&ususers='+user+'&usprop=editcount'+'&format=xml'
        editcount_xml = __query_wiki__(editcount_query)
        edit_count = __parse_wiki_xml__(editcount_xml, 'user', 'editcount')
        if edit_count >= min_editcount: 
            return user

def query_categories(res_id):
    ''' Returns the wikipedia categories of a wikipedia resource given its id '''
    categories_query = 'pageids='+str(res_id)+'&prop=categories&clshow=!hidden&format=xml'
    categories_xml = __query_wiki__(categories_query)
    categories = __parse_wiki_xml__(categories_xml, 'cl', 'title')
    formatted_categories = []
    for cat in categories:
        formatted_categories.append(__format_category__(cat))
    return formatted_categories

def __query_wiki__(query) : 
    ''' Queries wikipedia to retrieve various data in xml format '''
    hosturl = 'http://en.wikipedia.org/'
    queryaction = 'w/api.php?action=query&'
    result = urllib2.urlopen(hosturl+queryaction+query).read()
    return result

def __parse_wiki_xml__(wiki_xml, tag_name, attribute) : 
    ''' Parses xml fetched from wikipedia to retrieve the 
    value of the given attribute within the given tag. '''
    try:
        dom = xml.dom.minidom.parseString(wiki_xml)
        pages = dom.getElementsByTagName(tag_name)
    except:
        pages = []

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

def __format_category__(category):
    ''' Formats the category string in the following ways:
    1. remove leading and trailing white space 
    '''
    category = category.strip()
    return category
