from dataset_generation import pkl_util
import nltk

__output_str__ = 'extracting entities with NLTK'
def  __get_nltk_entities_cache_path__(site):
    return '/Users/elizabethmurnane/git/reslve/data/pickles/nltk_entities_cache_'+str(site.siteName)+'.pkl'     

def get_nltk_entity_cache(site):
    shorttext_entities = pkl_util.load_pickle(__output_str__, __get_nltk_entities_cache_path__(site))
    if shorttext_entities is None:
        shorttext_entities = {}    
    return shorttext_entities

def detectable_by_nltk(surface_form, shorttext_id, detected_entities_cache, entities_only=False):
    (noun_entities, named_entities) = detected_entities_cache[shorttext_id]
    
    # make everything lowercase for comparison
    noun_entities = [noun_ent.lower().decode('latin-1') for noun_ent in noun_entities]
    named_entities = [named_ent.lower().decode('latin-1') for named_ent in named_entities]
    surface_form = surface_form.lower()
    
    if (surface_form in named_entities or 
        surface_form in ' '.join(named_entities)):
        # surface form is a Named Entity
        return True
    
    if entities_only:
        # restricting to only entities and we just tested that it's not an entity
        return False
    
    return (surface_form in noun_entities or 
            surface_form in ' '.join(noun_entities))
    
def extract_entities(shorttext_rows, site):

    # { short text id -> (noun entities, named entities) }
    shorttext_entities = {}
    
    # nltk entity classes
    nltk_entity_types = __get_nltk_entity_types__()
    
    for shorttext_row in shorttext_rows:
        
        shorttext_id = shorttext_row[0]
        shorttext_str = shorttext_row[1]
        
        noun_entities = []
        named_entities = []
        
        sentences = nltk.sent_tokenize(shorttext_str)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.batch_ne_chunk(tagged_sentences)
        for tree in chunked_sentences:
            __extract_valid_entities__(tree, (noun_entities, named_entities), nltk_entity_types)    
            
        shorttext_entities[shorttext_id] = (noun_entities, named_entities)
        
    # Cache extracted entities
    pkl_util.write_pickle(__output_str__, shorttext_entities, __get_nltk_entities_cache_path__(site))
        
        
def __extract_valid_entities__(t, (noun_entities, named_entities), nltk_entity_types):
    ''' Extracts Named Entities and noun entities from the given nltk.Tree '''
    # extension of http://nltk.googlecode.com/svn/trunk/doc/api/nltk.sem.relextract-pysrc.html
    if hasattr(t, 'node') and t.node:
        if t.node in nltk_entity_types:
            named_entities.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                __extract_valid_entities__(child, (noun_entities, named_entities), nltk_entity_types)
    elif type(t) is tuple:
        if ('NN'==t[1] or 'NNS'==t[1] or 'NNP'==t[1] or 'NNPS'==t[1] or 'NP'==t[1]):
            noun_entities.append(t[0])
        elif t[0] in nltk_entity_types:
            named_entities.append(t[1])
    else: 
        raise

def __get_nltk_entity_types__():
    nltk_entity_types = []
    for class_list in nltk.sem.relextract.NE_CLASSES.values():
        nltk_entity_types.extend(class_list)
    return nltk_entity_types
