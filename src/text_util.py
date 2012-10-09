from nltk.corpus import stopwords
from nltk.tokenize.regexp import WordPunctTokenizer
from short_text_sources import short_text_websites
import nltk
import re
import string

def format_shorttext_for_NER(raw_shorttext, site):
    ''' Prepares the given short text for named entity extraction. Minimal 
    processing here to just remove line breaks, links, etc rather than more 
    substantial formatting like porting or stemming which will interfere with 
    NER toolkit's ability to recognize entities. '''
    
    ''' remove line breaks '''
    cleaned_text = raw_shorttext.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') 
    
    ''' remove html '''
    cleaned_text = nltk.clean_html(cleaned_text)
    
    ''' remove links (www.* or http*) '''
    cleaned_text = re.sub('((www\.[\s]+)|(https?://[^\s]+))','', cleaned_text)
    
    ''' replace double quotes with single quotes to avoid a Wikiminer error '''
    cleaned_text = cleaned_text.replace("\"", "\'")

    ''' remove non-printable characters '''
    cleaned_text = filter(lambda x: x in string.printable, cleaned_text) 
    
    ''' if Twitter:
    - replace hash tags with just the word, ie #cars -> cars 
    - remove RT string (which means retweet so we don't need to disambiguate it)
    - remove @mentions '''
    if short_text_websites.site_is_Twitter(site):
        
        # hash tags
        no_hash = []
        for word in cleaned_text.split():
            try:
                if word[0]=='#' and word[1] in string.ascii_letters:
                    word = word[1:] # remove the hash
            except:
                continue
            no_hash.append(word)
        cleaned_text = ' '.join(no_hash)
        
        # retweets and @mentions
        cleaned_text = ' '.join([word for word in cleaned_text.split() if 
                                 word.lower()!='rt' and 
                                 word[0]!='@'])
    
    ''' remove misc. remnant strings we don't care about '''
    words_manually_filter = []
    cleaned_text = ' '.join([word for word in cleaned_text.split() if not word in words_manually_filter])
    
    return cleaned_text

def get_nouns(raw_text, site):
    nouns = []
    try:
        cleaned_text = format_shorttext_for_NER(raw_text, site)
        text_tokens = nltk.word_tokenize(cleaned_text)
        for whatever in nltk.pos_tag(text_tokens):
            try:
                pos = whatever[1]
                if 'NN'==pos or 'NNS'==pos or 'NNP'==pos or 'NNPS'==pos or 'NP'==pos:
                    nouns.append(whatever[0])
            except:
                continue
    except: 
        return nouns
    return nouns