from nltk.corpus import stopwords
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.regexp import WordPunctTokenizer
from short_text_sources import short_text_websites
import nltk
import re
import string

def format_text_for_NER(raw_shorttext, site=None):
    ''' Prepares the given text for named entity extraction. Minimal 
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

#def is_english(raw_text, site):
#    ''' Returns true if the given text contains more English words than non-English words. 
#    (Not requiring *all* words to be English in order to allow for some misspellings, slang, etc). '''
#    num_english = 0
#    num_nonenglish = 0
#    cleaned_text = format_text_for_NER(raw_text, site)
#    cleaned_text = ' '.join(get_clean_BOW_doc(cleaned_text, False))
#    for word in cleaned_text.split():
#        if wordnet.synsets(word):
#            num_english = num_english+1
#        else:
#            num_nonenglish = num_nonenglish+1
#    prop_nonenglish = float(num_nonenglish)/float(num_english+num_nonenglish)
#    print prop_nonenglish
#    return (prop_nonenglish<.75)

def is_unwanted_automated_msg(surface_form, short_text):
    ''' Determine if this surface form conveys little semantic  
    information in an automated tweet that will merely be redundant. '''
    
    # unwanted entity like "video" in a msg like "I uploaded a YouTube video http://..."
    is_unwanted_youtube = (surface_form=='video' and (('I uploaded a' in short_text or 
                                                       'I favorited a' in short_text or 
                                                       'I liked a' in short_text) and
                                                      'YouTube video' in short_text))
    if is_unwanted_youtube:
        return True
    
    # unwanted entity like "sunny" in a msg like "Miami's weather forecast for tomorrow: Sunny"
    is_unwanted_weather = (surface_form.lower()=='sunny' and (('weather forecast for tomorrow:' in short_text)))
    if is_unwanted_weather:
        return True
    
    return False

def get_nouns(raw_text, site):
    nouns = []
    try:
        cleaned_text = format_text_for_NER(raw_text, site)
        text_tokens = WordPunctTokenizer().tokenize(cleaned_text)
        for token_and_POS in nltk.pos_tag(text_tokens):
            try:
                POS = token_and_POS[1]
                if 'NN'==POS or 'NNS'==POS or 'NNP'==POS or 'NNPS'==POS or 'NP'==POS:
                    nouns.append(token_and_POS[0])
            except:
                continue
    except: 
        return nouns
    return nouns

def get_clean_BOW_doc(doc):
    ''' Tokenizes and filters/formats the words in the given document to be used during 
    similarity measurement. This method should be used both when a doc goes into the  
    corpus and when a doc is being compared to another doc for similarity. 
    @return: a list of tokens '''
    stopset = set(stopwords.words('english'))
    stemmer = nltk.PorterStemmer()
    tokens = WordPunctTokenizer().tokenize(doc)
    non_punct = [''.join(ch for ch in token if not ch in string.punctuation) 
                    for token in tokens] # remove tokens that are purely punctuation
    clean_tokens = [token.lower() for token in non_punct if token.lower() not in stopset and len(token) > 2]
    final = [stemmer.stem(word) for word in clean_tokens]
    return final

def get_clean_doc(doc):
    ''' Joins the clean BOW back into a single string '''
    return ' '.join(get_clean_BOW_doc(doc))

def get_sentences(text):
    ''' Returns a list of the sentences in the given text '''
    sentences = PunktSentenceTokenizer().tokenize(text)
    return sentences