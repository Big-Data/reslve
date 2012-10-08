from nltk.corpus import stopwords
from nltk.downloader import Downloader
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
import re
import string

def get_clean_shorttext(raw_shorttext):
    cleaned_text = __format_text__(raw_shorttext)
    return cleaned_text

def __format_text__(raw_text):
    ''' Format the given string to filter out invalid strings '''
    
    ''' make all words lowercase '''
    cleaned_text = raw_text.lower()
    
    ''' remove line breaks '''
    cleaned_text = cleaned_text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ') 
    
    ''' remove html '''
    cleaned_text = nltk.clean_html(cleaned_text)
    
    ''' remove links (www.* or http*) '''
    cleaned_text = re.sub('((www\.[\s]+)|(https?://[^\s]+))','', cleaned_text)
    
    ''' remove numbers and punctuation '''# (but not contractions) '''
    punc = ['!', '$', '%', '&amp', ')', '(', '+', '*', ',', '.', ';', ':', '=', '<', '?', '>', '#', '[', ']', '\\', '_', '^', '`', '{', '}', '|', '~', "\"", "\'", "\"", "\'"]
    cleaned_text = ''.join(ch for ch in cleaned_text if not ch.isdigit() and ch not in punc)
    cleaned_text = ' '.join([word.lstrip("\"").lstrip("\'").rstrip("\"").rstrip("\'") for word in cleaned_text.split()])
    cleaned_text = ' '.join([word.lstrip("-").rstrip("-") for word in cleaned_text.split()])
    cleaned_text = ' '.join([word.lstrip("&").rstrip("&") for word in cleaned_text.split()])
    cleaned_text = cleaned_text.replace("//", " ").replace("\\", " ")
    
    ''' remove non-printable characters '''
    cleaned_text = filter(lambda x: x in string.printable, cleaned_text) 
    
    ''' remove English stop words and @ mentions '''
    eng_stopwords = stopwords.words('english')
    cleaned_text = ' '.join([word for word in cleaned_text.split() if word not in eng_stopwords and not word[0]=='@'])
    
    # commenting this out because articles aren't like casual/slang/etc 
    # user authored content that need this kind of processing
    #''' replace repeating letters with just two (ie "aaaaaaaaaand she said heeeeeey!") '''
    #repeat_pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    #text_string = ' '.join([repeat_pattern.sub(r"\1\1", word) for word in text_string.split()])
    
#    ''' lemmatize nouns, then verbs, then adjectives '''
#    wordnet_installed = Downloader().is_installed('wordnet')
#    if not wordnet_installed: 
#        nltk.download('wordnet')
#    lmtzr = WordNetLemmatizer()
#    cleaned_text = ' '.join([lmtzr.lemmatize(word) for word in cleaned_text.split()])
#    cleaned_text = ' '.join([lmtzr.lemmatize(word, 'v') for word in cleaned_text.split()])
#    cleaned_text = ' '.join([lmtzr.lemmatize(word, 'a') for word in cleaned_text.split()])
#    cleaned_text = ' '.join([lmtzr.lemmatize(word, 'r') for word in cleaned_text.split()])
    
#    # some words aren't being recognized by the lemmatizer? so do them manually..
#    text_string = text_string.replace('wrong_form', 'correct_form')
    
#    ''' remove words not found in an English dictionary '''
#    cleaned_text = ' '.join([word for word in cleaned_text.split() if enchant.Dict("en_US").check(word)])
    
    ''' remove isolated single characters '''
    cleaned_text = ' '.join([word for word in cleaned_text.split() if len(word)>1])
    
    ''' remove misc. remnant strings we don't care about '''
    words_manually_filter = []
    cleaned_text = ' '.join([word for word in cleaned_text.split() if not word in words_manually_filter])
    
    return cleaned_text