from CONSTANT_VARIABLES import RESLVE_DirectCategoryIdVsm, \
    RESLVE_DirectCategoryTitleBowVsm
from ranking_algorithms.vsm_algorithm import VSM_Algorithm
from wikipedia import wikipedia_api_util
import text_util

class DirectCategory_ID_VSM(VSM_Algorithm):
    ''' An algorithm with a similarity measure based on the
    ids of the categories of a candidate and the user matching '''
    
    def __init__(self):
        VSM_Algorithm.__init__(self, RESLVE_DirectCategoryIdVsm, "article direct parent categories' IDs", "directCatID")
    
    def get_article_representation(self, article_title):
        ''' Returns a list of ids of the categories of this article
        @return: a list of numbers '''
        category_titles = wikipedia_api_util.query_categories_of_res(article_title)
        category_ids = [wikipedia_api_util.query_page_id(cat_title) for cat_title in category_titles]
        return category_ids
    
class DirectCategory_TitleBOW_VSM(VSM_Algorithm):
    ''' An algorithm with a similarity measure based on the candidate's 
    category titles BOW and the user's category titles BOW '''
    
    def __init__(self):
        VSM_Algorithm.__init__(self, RESLVE_DirectCategoryTitleBowVsm, "article direct categories' titles BOW", "directCatTitleBOW")
    
    def get_article_representation(self, article_title):
        ''' Returns a bag of words build from the title
        of the categories of the given article.
        @return: a list of tokens '''
        category_titles = wikipedia_api_util.query_categories_of_res(article_title)
        category_titles_str = self.__format_category__(' '.join(category_titles))
        cleaned_titles = text_util.get_clean_BOW_doc(category_titles_str)
        return cleaned_titles
    
    def __format_category__(self, category_string):
        ''' Formats the category string in the following ways:
        - remove "Category:" prefix
        - remove leading and trailing white space 
        '''
        category_string = category_string.replace("Category:", "")
        category_string = category_string.strip()
        return category_string
