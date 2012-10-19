from ranking_algorithms.vsm_algorithm import VSM_Algorithm
from wikipedia import wikipedia_api_util
import text_util

''' TODO 
#def rank_articleBOW_VSM_numedits(candidates, username):
'''

class ArticleBOW_VSM(VSM_Algorithm):
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
