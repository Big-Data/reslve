from dataset_generation import wikipedia_edits_dataset_mgr
from wikipedia import wikipedia_api_util
import pickle

####### The RESLVE algorithm "Interface" #######
class RESLVE_Algorithm(object):
    ''' Main super class for all our algorithms '''
    
    def __init__(self, alg_type, usermodel_path):
        print "Initializing algorithm based on "+str(alg_type)
        self.alg_type = alg_type
        self.usermodel_path = '/Users/elizabethmurnane/git/reslve/data/pickles/usermodel_'+str(usermodel_path)+'.pkl'
    
    def get_user_doc(self, username, incorporate_edit_count=False):
        ''' Loads or creates+caches the user interest model '''
        user_models = self.__load_usermodels__(username)
        try:
            return user_models[username]
        except:
            return self.__init_user_doc__(username, user_models)
    def __load_usermodels__(self, username):
        try:
            print "Attempting to load "+str(self.alg_type)+" user model..."
            read_model = open(self.usermodel_path, 'rb')
            user_models = pickle.load(read_model)
            return user_models
        except:
            return {}
    def __init_user_doc__(self, username, user_models):
        ''' Returns a mapping from article representation to number
        of times the given user has made non-trivial edits on that article. '''
        # Model for user doesn't exist yet, so create it
        print "Model for user "+username+" not yet created, so creating and caching..."
        
        user_doc = []
        
        # get article representation for each article user edited and cache it
        # along with the number of times the user edited that page
        articleids_to_numedits = wikipedia_edits_dataset_mgr.get_edits_by_user(username)
        if len(articleids_to_numedits)==0:
            # no edits by user yet, so make sure those 
            # have been fetched and stored in the dataset
            print "No edits by user "+str(username)+\
            " cached yet, so fetching those now and adding to edits dataset..."
            wikipedia_edits_dataset_mgr.build_edits_by_user(username)
            articleids_to_numedits = wikipedia_edits_dataset_mgr.get_edits_by_user(username)
        
        print "Processing edited articles to build user model..."
        progress_count = 1
        progress_finish = len(articleids_to_numedits)
        for article_id in articleids_to_numedits:
            
            if progress_count%10==0:
                print "Added "+str(progress_count)+" articles out of "+str(progress_finish)+" to user model..."
            progress_count = progress_count+1
            
            # get the article features
            article_title = wikipedia_api_util.query_page_title(article_id)
            article_model = self.get_article_representation(article_title)
            user_doc.extend(article_model)
        
        user_models[username] = user_doc
        # and save to file
        write_pkl = open(self.usermodel_path, 'wb')
        pickle.dump(user_models, write_pkl)
        write_pkl.close()
        
        print "Finished adding all articles to user model and caching it"
        return user_doc
    