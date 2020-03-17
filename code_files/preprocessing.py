# -*- coding: utf-8 -*-

import string
from string import maketrans
import re


sw_filename = 'dictionaries/greekstopwords.txt'
pos_filename = 'dictionaries/pos_lex.txt'
neg_filename = 'dictionaries/neg_lex.txt'

# initializes dictionary of words from file of words
def init_dict(filename):
    import codecs
    f = codecs.open(filename, encoding='utf-8')
    sw = []
    dict_sw = {}
    for line in f.readlines():
        words = line.split(',')
        if len(words) == 2:
            dict_sw[words[0].strip('\n\r\t ')] = words[1]
        sw.append(words[0].strip('\n\r\t '))
    return sw, dict_sw

# returns whether the tweet is not a retweet and it is from greek lang
def keep_tweet(tweet):
    return (tweet['lang'] == 'el') and (not tweet['retweeted']) and (not tweet['text'].startswith('RT'))

'''
filters out retweets and tweets with local or location different to greek
using function keep_tweet
'''
def filtering(tweets):
    tw = []
    for tweet in tweets:
        if keep_tweet(tweet):
            tw.append(tweet)
    return tw

# cleans the tweet from whitespace, punctuation and emphasis, converts it to whitespace and reserves only greek words
def cleanning(text):
    tw = clean_whitespace(text)
    tw = clean_punctuation(tw)
    tw = toUpper(tw)
    stopwords, empty_dict = init_dict(sw_filename)
    clean_tw = ''
    for w in tw.split(' '):
        w = w.encode('utf-8').strip()
        if isGreek(w) and  (w.decode('utf-8') not  in stopwords):
            clean_tw += ' '+stemming(w)

    return clean_tw

# applies stemming on term
def stemming(term):
    three_letter = ["ΟΥΣ", "ΕΙΣ", "ΕΩΝ", "ΟΥΝ"]
    two_letter = ["ΟΣ","ΗΣ", "ΕΣ", "ΩΝ", "ΟΥ", "ΟΙ", "ΑΣ", "ΩΣ", "ΑΙ","ΥΣ", "ΟΝ", "ΑΝ", "ΕΙ"]
    one_letter = ["Α", "Η", "Ο", "Ε", "Ω", "Υ", "Ι"]
    stemmed = term
    if (len(term) >= 4):
        #this is because words are unicode encoded.. we could decode and work as usual but this is easier
        if term[-6:] in three_letter:
            stemmed = term[:-6]
        elif term[-4:] in two_letter:
            stemmed = term[:-4]
        elif term[-2:] in one_letter:
            stemmed = term[:-2]

    return stemmed

# converts text to upper case without emphasis
def toUpper(text):
    text = text.decode('utf-8').upper()
    letter_cleaning = {u'Ά':u'Α', u'Έ':u'Ε', u'Ή':u'Η', u'Ί':u'Ι', u'Ό':u'Ο', u'Ύ':u'Υ', u'Ώ':u'Ω'}
    for letter in letter_cleaning.keys():
        text = text.replace(letter, letter_cleaning[letter])

    return text

# converts every punctuation to space
def clean_punctuation(text):
    tr = maketrans(string.punctuation, "                                ")
    return text.translate(tr)
    #with this urls are broken into parts...however these parts will be dropped later as only greek words are kept

# converts every whitespace to space so as to help splitting the tweet into parts
def clean_whitespace(text):
    tr = maketrans(string.whitespace, "      ")
    return text.translate(tr)

# decides whether or not the word consists of greek letters
def isGreek(word):
    return re.match('^[ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]+$', word) != None
