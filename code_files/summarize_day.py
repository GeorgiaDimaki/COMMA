# -*- coding: utf-8 -*-

# summarize_day.py #################################################################################################

from preprocessing import *

neg_w, neg_dict = init_dict('dictionaries/neg_lex.txt')
pos_w, pos_dict = init_dict('dictionaries/pos_lex.txt')

# makes a summary of the tweets given for the specific day given.
# used to create daily summary
# this method does not care for tweet category. to work properly please provide only tweets from a specific category
def sumarize(date, tweets):

    total_unfiltered = len(tweets)
    new_list = filtering(tweets)
    all_tweets = []
    neg_tw = 0
    pos_tw = 0
    neu_tw = 0
    for tweet in new_list:

        t = cleanning(tweet['text'].encode('utf-8'))

        if t.decode('utf-8') in all_tweets:
            continue
        else:
            all_tweets.append(t.decode('utf-8'))
            neg, pos = calculateNegPos(t)
            if neg > pos:
                neg_tw += 1
            elif neg < pos:
                pos_tw += 1
            else:
                neu_tw += 1

    total_filtered = len(all_tweets)
    result = {'date':str(date), 'pos': pos_tw, 'neg': neg_tw, 'neu': neu_tw,
              'total_unfiltered': total_unfiltered, 'total_filtered': total_filtered, 'tweets':all_tweets}
    return result

# counts positive and negative words in a tweet cleaned text
def calculateNegPos(tweet):

    neg = 0
    pos = 0

    for term in tweet.split(' '):
        if term.decode('utf-8') in neg_w:
            neg += 1

        if term.decode('utf-8') in pos_w:
            pos += 1

    return  neg, pos
