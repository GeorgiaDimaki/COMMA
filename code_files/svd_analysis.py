from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import scipy

# returns all filtered tweets from the weekNum given or from the whole collection if no weekNum given
# only for memory stored collection
def get_all_filtered(memory_db , weekNum = None):
    filtered = []

    if weekNum:
        for week in memory_db:
            if week['_id'] == weekNum:
                for category in week['collected']:
                    for day in category['days']:
                        filtered.extend(day['tweets'])
    else:
        for week in memory_db:
            for category in week['collected']:
                for day in category['days']:
                    filtered.extend(day['tweets'])

    return  filtered

# 1) finds all unique terms that appear in tweets more than two times
# 2) counts how many times they appear in every tweet
# 3) calculates tfidf values for every word found
# 4) performs svd to the table of term x tweet and keeps only 300 dimensions
# 5) normalizes table U that represents terms with the L2 norm
# 6) returns normalized U and the vocabulary of unique terms
def svd_analyze(memory_db, weekNum = None):
    vectorizer =TfidfVectorizer(min_df=2, lowercase=False, norm=None)
    tweets = get_all_filtered(memory_db, weekNum)
    X = vectorizer.fit_transform(tweets)
    U, sigma, V = scipy.sparse.linalg.svds(X.asfptype().T, k=300)
    voc = dict((v,k) for k, v in vectorizer.vocabulary_.iteritems())
    for i in range(U.shape[0]):
        L2 = np.linalg.norm(U[i,:])
        if not L2==0:
            U[i,:] /= L2
    return U, voc

# prints words in num_columns columns. Helper function used to print results.
def print_in_columns(words, num_columns):
    import sys
    i = 1
    for w in words:
        sys.stdout.write( u'{0:<20}'.format(w))
        if i%num_columns == 0 :
            sys.stdout.flush()
            print "\n"
        i += 1
    sys.stdout.flush()

# given a term to term similarity matrix finds the each term neighborhood of size n_num and for each
# neighbor decides if its positive or negative based on term and dictionaries negLex and posLex.
# afterwards it prints the new positive and negative sets created and calculates how many of the words they
# contain are actually positive or negative respectively
def neighbors(term2term_similarity, n_num, voc, neglex, poslex):

    def conclusion(word, neighborhood, lex):
        new = []
        for n in neighborhood:
            if not (n in lex):
                new.append(n)

        return new

    in_neg = 0
    in_pos = 0
    new_neg = []
    new_pos = []
    pos_terms = 0
    neg_terms = 0
    for i in range(term2term_similarity.shape[0]):
        best = np.argsort(term2term_similarity[i, :])
        best =  best[~(best == i)]

        if not (voc[i] in neglex) and not (voc[i] in poslex):
            continue

        neighborhood = []
        for j in range(1, n_num + 1):
            neighborhood.append(voc[best[-1*j]])

        if voc[i] in neglex:
            neg_terms += 1
            new = conclusion(voc[i], neighborhood, neglex)
            in_neg += len(neighborhood) - len(new)
            new_neg.extend(new)
        else:
            pos_terms += 1
            new =  conclusion(voc[i], neighborhood, poslex)
            in_pos += len(neighborhood) - len(new)
            new_pos.extend(new)

    new_neg = list(set(new_neg))
    new_neg.sort()
    new_pos = list(set(new_pos))
    new_pos.sort()
    if pos_terms != 0:
        in_pos /= float(pos_terms)
    if neg_terms != 0:
        in_neg /= float(neg_terms)

    print "\n**********************************************************************************************"
    print "\nFor ",n_num," neighbors: \n"
    print "New positive words' set: \n"
    print_in_columns(new_pos, 5)

    print "\n\nNew negative words' set: \n"
    print_in_columns(new_neg, 5)

    print "\n\nAverage number of words in PosLex: ", in_pos
    print "\nAverage number of words in NegLex: ", in_neg

    return  in_pos, in_neg