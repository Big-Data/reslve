'''
Functions to query Wikipedia API for various 
pieces of information and functions to parse results
'''
from CONSTANT_VARIABLES import ACTIVE_WIKIPEDIA_MIN
import urllib2
import xml.dom.minidom

def query_editors_of_recentchanges(desired_num_editors_to_fetch, recent_editors, active_users_only=True):
    ''' Fetch the most recently edited pages on 
    Wikipedia and returns a set of unique usernames
    for the users who made those edits. 
    @param recent_editors: editors already cached 
    @param active_users_only: True if only want to return editors who have 
    made non-trivial edits on a minimum number of Wikipedia pages '''
    
    print "Querying Wikipedia for editors who recently made changes..."
    
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
    
    count = 1
    rcstart = ''
    while len(recent_editors) < desired_num_editors_to_fetch:
        try:
            # can request up to 5000 but just do..500? unless even more usernames than that desired
            num_left_to_fetch = desired_num_editors_to_fetch - len(recent_editors)
            rclimit_val = max(500, num_left_to_fetch)
            rclimit = '&rclimit='+str(min(5000, rclimit_val))
            
            # query wiki for recent edits
            params = rclimit+rctype+rcshow+rcprop+rcdir+rcstart
            query = 'list=recentchanges'+params+'&format=xml'
            recent_edits_xml = __query_wiki__(query)
            
            # parse the results to get the users who made these edits
            users = __parse_wiki_xml__(recent_edits_xml, 'rc', 'user')
            for editor in users:
                
                if len(recent_editors) >= desired_num_editors_to_fetch:
                    break # fetched enough new active editors
                
                # just output some progress..
                if count%5==0:
                    print "Querying for recent editors... Encountered so far: "+str(count)+\
                    ". Mapped so far: "+str(len(recent_editors))
                count = count+1
                
                try:
                    if editor in recent_editors:
                        continue # already mapped this user
                    
                    if (str(editor).replace('.', '')).isdigit() :
                        continue # ignore IP addresses
                    
                    # get map of pages user edited -> number of times edited page
                    edits_map = query_usercontribs(editor, False)
                    
                    if active_users_only and (len(edits_map.keys())<ACTIVE_WIKIPEDIA_MIN):
                        # ignore editors that haven't made non-trivial 
                        # edits on the minimum number of pages
                        continue
                    
                    recent_editors.append(editor)
                except:
                    continue # ignore problematic editors
            
            query_continue = __wiki_xml_has_tag__(recent_edits_xml, 'query-continue')  
            if not query_continue:
                break
            next_changes = __parse_wiki_xml__(recent_edits_xml, 'recentchanges', 'rcstart')
            rcstart = '&rcstart='+next_changes[0]
        except Exception as e:
            print "Unexpected exception while querying for recent wikipedia edits ",e
            break

    return recent_editors

def query_username_SpecialRandom():
    ''' Returns a random wikipedia username or None if an 
    unexpected error occurs using a Special:Random/User query '''
    try:
        rand_user_req_url = 'http://en.wikipedia.org/wiki/Special:Random/User'
        req = urllib2.Request(rand_user_req_url, headers={'User-Agent' : "Browser"})
        user_url_str = str(urllib2.urlopen(req).geturl())
        user_namespace = 'User:'
        pos = user_url_str.find(user_namespace)
        if pos==-1:
            return None
        
        username = user_url_str[pos+len(user_namespace):]
        extra_path = '/'
        extra_pos = username.find(extra_path)
        if extra_pos!=-1:
            username = username[0:extra_pos]
        return username
    except:
        return None

def query_usercontribs(username, fetch_all_contribs):
    '''Returns a mapping from page id -> number of times given user has edited that page
    @param fetch_all_contribs: True if we want to fetch and return all pages edited by a 
    user, False if we only want to return ACTIVE_WIKIPEDIA_MIN number of edited pages '''
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
        if not fetch_all_contribs and len(page_to_numedits)>=ACTIVE_WIKIPEDIA_MIN:
            # not fetching all user's edited pages so just 
            # fetch the minimum required to be considered active
            return page_to_numedits
        
        edits_query = 'list=usercontribs&ucuser='+username+'&uclimit=500'+ucnamespace+ucshow+'&format=xml'+ucstart
        user_edits_xml = __query_wiki__(edits_query)
        edited_pages = __parse_wiki_xml__(user_edits_xml, 'item', 'pageid', True)
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

def query_page_revisions(page_id):
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
        if len(next_revisions)==0:
            break
        rvstart = '&rvstartid='+next_revisions[0]
    
    return total_num_edits

def query_total_edits_siteinfo():
    ''' Returns the total number of edits made on Wikipedia '''
    stats_query = 'meta=siteinfo&siprop=statistics&format=xml'
    stats_xml = __query_wiki__(stats_query)
    edit_stat = __parse_wiki_xml__(stats_xml, 'statistics', 'edits')
    return edit_stat

def query_categories_of_res(res_id):
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

def __parse_wiki_xml__(wiki_xml, tag_name, attribute, allow_duplicate_attr_vals=False) : 
    ''' Parses xml fetched from wikipedia to retrieve the 
    value of the given attribute within the given tag. '''
    try:
        dom = xml.dom.minidom.parseString(wiki_xml)
        elmts = dom.getElementsByTagName(tag_name)
    except:
        elmts = []

    attr_list = []
    for elmt in elmts : 
        try:
            if elmt.hasAttribute(attribute):
                attr = elmt.getAttribute(attribute)
                attr_list.append(attr)
        except:
            continue # ignore problematic elements
        
    if not allow_duplicate_attr_vals:
        attr_list = list(set(attr_list)) # remove duplicates
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