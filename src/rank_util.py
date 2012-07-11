from collections import defaultdict
from numpy.lib.scimath import sqrt
import math

# Computes similarity based on binary absense or presense 
# of terms rather than the frequency of terms. Each of the
# given lists should be a list of the words in that document.
# See http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/tani.html
def jaccard_similarity(doc1_words, doc2_words):
    intersection = [common_word for common_word in doc1_words if common_word in doc2_words]
    return float(len(intersection))/(len(doc1_words) + len(doc2_words) - len(intersection))    

def dot(a,b):
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * b[i];
    return sum_val

def norm(a):
    n = len(a)
    sum_val = 0
    for i in xrange(n):
        sum_val += a[i] * a[i]
    return math.sqrt(sum_val)

def cossim(a,b):
    return dot(a,b) / (norm(a) * norm(b))
  
# See http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/sphilip/cos.html
def cosine_similarity(doc_vector1, doc_vector2):
    # Calculate numerator of cosine similarity
    dot = [doc_vector1[i] * doc_vector2[i] for i in range(len(doc_vector1))]
  
    # Normalize the first vector
    sum_vector1 = 0.0
    print range(len(doc_vector1))
    sum_vector1 += sum_vector1 + (doc_vector1[i]*doc_vector1[i] for i in range(len(doc_vector1)))
    norm_vector1 = sqrt(sum_vector1)
  
    # Normalize the second vector
    sum_vector2 = 0.0
    sum_vector2 += sum_vector2 + (doc_vector2[i]*doc_vector2[i] for i in range(len(doc_vector2)))
    norm_vector2 = sqrt(sum_vector2)
  
    return (dot/(norm_vector1*norm_vector2))

def make_freq_vector(doc):
    doc_words = doc.split()
    freq_vector = defaultdict(int)
    for word in doc_words:
        freq_vector[word]+=1
    return freq_vector
