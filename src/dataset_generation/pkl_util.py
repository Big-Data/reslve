""" Functions to dump and load from dataset cache pkl files """

from CONSTANT_VARIABLES import DEBUG_ON
import pickle

def load_pickle(pkl_load_str, pkl_path):
    ''' Prints given output to the console, then loads and 
    returns the pkl file located at the given path '''
    print "Loading cache of "+str(pkl_load_str)
    try:
        read_pkl = open(pkl_path, 'rb')
        cache = pickle.load(read_pkl)
    except:
        cache = None
    return cache

def write_pickle(pkl_write_str, data_to_cache, pkl_path):
    ''' Prints given output to the console, then writes
    the given data to a pkl file located at the given path '''
    if DEBUG_ON:
        print "Debug turned on, so not writing pkl of "+pkl_write_str
        return
    
    print "Writing to cache "+str(pkl_write_str)
    write_pkl = open(pkl_path, 'wb')
    pickle.dump(data_to_cache, write_pkl)
    write_pkl.close()