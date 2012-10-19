from ranking_algorithms.vsm_algorithm import VSM_Algorithm
from wikipedia import wikipedia_api_util
import text_util

''' TODO 
#def rank_articleBOW_VSM_numedits(candidates, username):
'''

class Article_ContentBOW_VSM(VSM_Algorithm):
    ''' An algorithm with a similarity measure between the BOW of the candidate 
    resource's article page and the BOW of the user's edited articles' pages '''
    
    def __init__(self):
        VSM_Algorithm.__init__(self, "article Bag-of-Words", "articleBOW-VSM")
    
    def get_article_representation(self, article_title):
        ''' Returns a bag of words build from the text content
        on the given article.
        @return: a list of tokens '''
        article_text = wikipedia_api_util.query_page_content_text(article_title) # get the text of the article's page
        cleaned_tokens = text_util.get_clean_BOW_doc(article_text) # clean the article text 
        return cleaned_tokens

    
class Article_ID_VSM(VSM_Algorithm):
    ''' An algorithm with a similarity measure based on the
    candidate article's ID and the user's edited articles' IDs matching.
    In other words, this algorithm will only result in non-zero
    similarity measures for candidates that correspond to articles
    the user has edited. '''
    
    def __init__(self):
        VSM_Algorithm.__init__(self, "article ID", "articleID")
    
    def get_article_representation(self, article_title):
        ''' Returns a list containing the id of this article
        @return: a list of numbers '''
        article_model = [wikipedia_api_util.query_page_id(article_title)]
        return article_model
    
class Article_TitleBOW_VSM(VSM_Algorithm):
    ''' An algorithm with a similarity measure based on the candidate's 
    article title BOW and the user's articles' titles BOW. In other words,
    this algorithm measures how many words in a candidate article's title
    overlap with words in titles of articles the user has edited. '''
    
    def __init__(self):
        VSM_Algorithm.__init__(self, "article's title BOW", "articleTitleBOW")
    
    def get_article_representation(self, article_title):
        ''' Returns a bag of words build from the title of the given article.
        @return: a list of tokens '''
        article_title_str = article_title.replace('_', ' ')
        cleaned_title = text_util.get_clean_BOW_doc(article_title_str)
        return cleaned_title
