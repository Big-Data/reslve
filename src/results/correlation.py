''' Looks at a disambiguation strategy's accuracy as a function of the length of 
a short text. We expect shorter texts will correlate with lower accuracies for traditional
strategies but that RESLVE algorithms will maintain higher performance levels regardless. '''

from collections import OrderedDict
from nltk.compat import defaultdict
from short_text_sources.short_text_websites import get_twitter_site
import RESLVE_rankings_mgr
import codecs
import csv
import math
import numpy

__accuracy_vs_x_spreadsheet__ = '/Users/elizabethmurnane/git/reslve/data/analysis/accuracy_vs_x.csv'
__shorttext_length_distribution__ = '/Users/elizabethmurnane/git/reslve/data/analysis/shorttext_len_freq_dist.csv'

def run_correlation_analysis():
    site = get_twitter_site()
    accuracy_correlations(site)
    
def accuracy_correlations(site):
    ''' Measures correlation between the length of the short text
    an entity is contained in and the accuracy with which that 
    entity is resolved by RESLVE and by baselines. '''
    
    binned_entities = get_binned_entities(site)    
    rows = []
    headers = ["Short text length",
               "Wikipedia Miner Accuracy", "DBPedia Spotlight Accuracy", 
               "RESLVE Accuracy", "Human Consensus"]
    rows.append(headers)
    for bin_end in binned_entities:
        print "Trying to compute accuracy on short texts up to length "+str(bin_end)
        
        # compute accuracy with each strategy
        wikiminer_correct = 0
        dbpedia_correct = 0
        reslve_correct = 0
        human_consensus = 0
        
        total_evaluated = 0
        
        entities = binned_entities[bin_end]
        print "Number of entities in this bin: "+str(len(entities))+" "+str([entity.ne_obj.get_entity_id() for entity in entities])
        for resolved_entity in entities:
            if resolved_entity.is_baseline_wikiminer_correct():
                wikiminer_correct = wikiminer_correct+1
            if resolved_entity.is_baseline_dbpedia_correct():
                dbpedia_correct = dbpedia_correct+1
            if resolved_entity.is_reslve_correct(resolved_entity.reslve_rankings.keys()[0]):
                reslve_correct = reslve_correct+1
            if len(resolved_entity.get_unanimous_candidates_goldstandard())>0:
                human_consensus = human_consensus+1
            total_evaluated=total_evaluated+1
            
        if total_evaluated==0:
            continue # no short texts in this bin?

        wikiminer_accuracy = float(wikiminer_correct)/float(total_evaluated)
        dbpedia_accuracy = float(dbpedia_correct)/float(total_evaluated)
        reslve_accuracy = float(reslve_correct)/float(total_evaluated)
        human_able = float(human_consensus)/float(total_evaluated)
        
        row = [math.ceil(bin_end), wikiminer_accuracy, dbpedia_accuracy, reslve_accuracy, human_able]
        rows.append(row)

    f = codecs.open(__accuracy_vs_x_spreadsheet__, 'wb', encoding="utf-8")
    csv_writer = csv.writer(f, dialect=csv.excel)
    for row in rows:
        csv_writer.writerow(row)

def get_binned_entities(site):
    ''' Builds a frequency distribution of short text length for a histogram. '''
        
    # Get the frequencies of each short text length
    freq_dist = defaultdict(list)
    num_observations = 0
    resolved_entities = RESLVE_rankings_mgr.get_resolved_entities(site, False)
    print str(len(resolved_entities))
    for resolved_entity in resolved_entities:
        shorttext_length = len(resolved_entity.ne_obj.shorttext_str)
        freq_dist[shorttext_length].append(resolved_entity)
        num_observations = num_observations+1
    freq_dist = OrderedDict(sorted(freq_dist.iteritems())) # sort in ascending order of text length
    print "Freq Dist: "+str(freq_dist.keys())
        
    # Make bins mapping a key equal to maximum length 
    # of all the short texts in the value list
    binned_entities = {}
    shorttext_lengths = freq_dist.keys()
    max_len = max(shorttext_lengths)
    min_len = min(shorttext_lengths)
    print "Max and min length: "+str(max_len)+", "+str(min_len)
    
    # NOTE: Consider the alternatives below for k and 
    # bin width once know the distribution of the data
    
    # number of bins - be sure to use formula appropriate for distribution
    k = __get_num_bins_sturges__(num_observations) # sturges' (assumes approx. normal dist)
    #k = __get_num_bins__(num_observations)
    print "Number of bins (according to Sturges'): "+str(k)
    
    # bin width according to Freedman-Diaconis rule
    #bin_width = math.ceil(2 * __interquartile_range__(shorttext_lengths) * (1/__cube_root__(num_observations)))
    #bin_width = math.ceil(1/__cube_root__(num_observations))*__std_dev__(shorttext_lengths)*3.49
    bin_width = math.ceil((max_len-min_len)/k)
    print "Bin width: "+str(bin_width)
    
    bin_start = min_len
    while bin_start < max_len:
        print "bin start: "+str(bin_start)
        bin_end = min(bin_start+bin_width, max_len) # don't go over the max length
        print "bin end: "+str(bin_end)
        bin_list = []
        for key in freq_dist:
            if key >= bin_start and (key < bin_end 
                                     or # this or is to handle the max end of the bins
                                     (bin_end==max_len and key <= bin_end)): 
                bin_list.extend(freq_dist[key])
        binned_entities[bin_end] = bin_list
        bin_start = min(bin_start+bin_width, max_len)
    binned_entities = OrderedDict(sorted(binned_entities.iteritems())) # sort
    print "Created "+str(len(binned_entities))+" bins: "+str(binned_entities)
    
    rows = []
    headers = ["Frequency", "Short text length"]
    rows.append(headers)
    for bin_end in binned_entities:
        num_entities_in_bin = len(binned_entities[bin_end])
        row = [num_entities_in_bin, bin_end]
        rows.append(row)
    f = codecs.open(__shorttext_length_distribution__, 'wb', encoding="utf-8")
    csv_writer = csv.writer(f, dialect=csv.excel)
    for row in rows:
        csv_writer.writerow(row)
        
    return binned_entities

def __get_num_bins_sturges__(num_observations):
    k = math.ceil(math.log(num_observations, 2)+1)
    return k

def __get_num_bins__(num_observations):
    ''' 2^(n-1) < a < 2^n where a = size of dataset --> n = ln(a) / ln(2) '''
    return math.log(num_observations) /  math.log(2)

def __cube_root__(n):
    return math.pow(n,1.0/3)

def __std_dev__(x):
    # from http://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = math.sqrt(std / float(n-1))
    return std

def __interquartile_range__(num_list):
    sorted_num_list = sorted(num_list)
    if len(sorted_num_list)%2==0:
        median_index = len(sorted_num_list)/2
    else:
        median_index = sorted_num_list.index(numpy.median(sorted_num_list))
    q1 = numpy.median(sorted_num_list[:median_index])
    q3 = numpy.median(sorted_num_list[median_index:])
    return q3-q1

run_correlation_analysis()
