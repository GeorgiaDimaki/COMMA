# -*- coding: utf-8 -*-

# !!! requires pymongo installed

import tweepy
from pymongo.errors import WriteError
from tweepy import OAuthHandler
from summarize_day import *
import time
from dateutil import parser
from datetime import date
from db_helpers import *

############### globals #########################
# reminders
reminder_file_comma1 = "reminders/reminder_comma1.txt"
reminder_file_comma2 = "reminders/reminder_comma2.txt"
reminder_file_leader1 = "reminders/reminder_leader1.txt"
reminder_file_leader2 = "reminders/reminder_leader2.txt"
# queries
query_comma1 =  '#syriza -#ND'
query_comma2 = '#ND -#syriza'
query_leader1 = '@tsipras'
query_leader2 = '@mitsotakis'
# categories
category_comma1 = '#syriza'
category_comma2 = '#nd'
category_leader1 = '@tsipras'
category_leader2 = '@mitsotakis'
# database
db_name = 'tweetdb'
# collections
collection_name = 'COMMA_round2_tweets'
collection_week = 'week'
# the date collecting started
first = date(2016,12,18)

def initApi():

    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_secret = ''

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    return tweepy.API(auth)

# ### the file will have the above format:
#
# <line 1> maxPrev   (max_id = the maximum id found in the tweets collected.)
# (the above lines present in file only in cases we want to "loop back in the past" to get tweets we could not
# collect because the limit of requests to Twitter was reached.)
# <line 2> min_id   (min_id = the minimun id found in the tweets collected.)
# <line 3> maxPrev  (maxPrev = the maximum id found in the tweets at a previous collection round.)
#
# ####
def saveReminders(max_id, min_id, maxPrev, filename):
    print 'saving the max id from tweets collected!', max_id
    f = open(filename, 'w+')
    f.write(str(max_id)+'\n')
    if min_id and max_id: # in order to write nothing if min_id is None (otherwise it writes "None")
        f.write(str(min_id)+'\n'+str(maxPrev))
    f.close()

def loadReminders(filename):
    f = open(filename, 'r+')

    max = -1000
    min = None
    maxPrev = None

    lines =  f.readlines()
    for i in range(len(lines)):
        if i==0:
            max = int(lines[i].rstrip('\n'))
        elif i==1:
            min = int(lines[i].rstrip('\n'))
        else:
            maxPrev = int(lines[i].rstrip('\n'))

    f.close()

    return max, min, maxPrev


def show_report(collected, duplicates, total_found, num_searches):

    print collected,' tweets collected'
    print duplicates, ' duplicate tweets'
    print total_found, ' total tweets found'
    print 'searches: ', num_searches


# updates weeks collection with in order to include the new summarized results of list_of_tweets
def updateWeek(db, date, category, list_of_tweets):

    weeknum = (date-first).days/7
    if(db[collection_week].find({'_id':weeknum, 'collected.category': category}).count() == 0):
        if(db[collection_week].find({'_id':weeknum}).count() == 0):
            db[collection_week].insert({'_id':weeknum, 'collected': [{'category': category, 'days':[]}] })
        else:
            db[collection_week].update_one({'_id':weeknum}, {'$push' : { 'collected' : {'category': category, 'days':[]} }})

    result = sumarize(date, list_of_tweets)

    try:
        res=db[collection_week].find(
              {'_id':weeknum, 'collected.category': category},
              {'collected.$.days':1})

        i= 0
        index = None

        for item in res[0]['collected'][0]['days']:
            if item['date'] == str(date):
                index = i
            i += 1

        if index:
            db[collection_week].update(
              {'_id':weeknum, 'collected.category': category},
              {'$inc' : {'collected.$.days.'+str(index)+".pos" : int(result['pos']),
                          'collected.$.days.'+str(index)+".neg" : int(result['neg']),
                          'collected.$.days.'+str(index)+".neu" : int(result['neu']),
                          'collected.$.days.'+str(index)+".total_unfiltered": int(result['total_unfiltered']),
                          'collected.$.days.'+str(index)+".total_filtered" : int(result['total_filtered'])} })
            db[collection_week].update_one({'_id': weeknum, 'collected.category': category },
                                          {'$addToSet':{'collected.$.days.'+str(index)+".tweets" : {'$each' : result['tweets']}}})
        else:
            db[collection_week].update_one({'_id': weeknum, 'collected.category': category}, {'$addToSet':{'collected.$.days' : result}})

    except WriteError as e:
        print e.message

def collect(query, category, db_name, collection_name, reminder_file):

    api = initApi()

    #this will either access the comma_tweets database or create it depending on its existance
    client, db = connectToDB(db_name)

    if client == None:
        exit(0)

    maxId, minId, maxPrev = loadReminders(reminder_file)

    # maxPrev actually represents the lower bound in our search in order not to retrieve tweets already retrieved (duplicate id)
    # if we are "looping back in past" then it has a value already but if we don't it will be None.
    if maxPrev == None: # it is used in searches thus it must be initialized correctly
        maxPrev = maxId

    #collecting data

    collecting = True
    collected = 0
    searches = 0
    count = 0 # counts the times no results found
    duplicates = 0
    total_tweets_found = 0
    reset_bounds = False

    print "Waiting for results..."
    while collecting:

        reset_bounds = False

        try:
            # searches for tweets between maxPrev (max from previous searches)
            # and current maxId found (the maxId found at the first iteration of the above while)
            # minId is used to create a limit to our search so that we can move backwards.
            # this is more important for the first run of the program every day.
            # it can find all the tweets that happened between the two runs of the program.
            while True:

                if minId: # so as to loop back correctly
                    minId -=1

                new_tweets = api.search(q=query, since_id=maxPrev, max_id = minId,count=100)
                searches += 1


                if new_tweets:

                    total_tweets_found += len(new_tweets)
                    date = {}
                    minId = new_tweets[0]

                    for tw in new_tweets:
                        tw_id = int(tw._json['id'])

                        if tw_id > maxId:
                            maxId = tw_id

                        if tw_id < minId:
                            minId = tw_id

                        try:
                            inserted = tw._json
                            inserted['_id'] = tw_id
                            inserted['category'] = category
                            db[collection_name].insert(inserted)
                            collected +=1

                            d = parser.parse(inserted["created_at"])
                            if d.date() not in date.keys():
                                date[d.date()] = []

                            date[d.date()].append(inserted)

                        except pymongo.errors.DuplicateKeyError:
                            duplicates+=1
                            pass

                    for d in date.keys():
                        updateWeek(db, d,collection_name, date[d])


                    if minId <= maxPrev:
                        print "limit reached"
                        reset_bounds = True
                        break

                else:
                    count += 1
                    reset_bounds = True
                    # if no more tweets are returned after two iterations we stop the whole process.
                    # otherwise it will spin lock until the request for tweets bound is reached.
                    if count == 2:
                        collecting = False
                    break

            if reset_bounds:
                # when the loop breaks these two lines are executed
                maxPrev = maxId
                minId = None

        except tweepy.TweepError as e:
            # basically is an RateLimitReached.
            # However although it seems to be the only one that occurs i chose TweepError as the caught error
            # to be ready for other type of errors that might occur
            collecting = False

    if reset_bounds:
        saveReminders(maxId, None, None, reminder_file)
    else:
        saveReminders(maxId, minId, maxPrev, reminder_file)

    client.close()
    show_report(collected,duplicates,total_tweets_found,searches)

##### COLLECTING #############################################################################################

i = 0;
while True:
    cur = i%4
    print "iteration ", i
    if cur == 0:
        collect(query_comma1, category_comma1, db_name, collection_name, reminder_file_comma1)
    elif cur == 1:
        collect(query_comma2, category_comma2, db_name, collection_name, reminder_file_comma2)
    elif cur == 2:
        collect(query_leader1, category_leader1, db_name, collection_name, reminder_file_leader1)
    else:
        collect(query_leader2, category_leader2, db_name, collection_name, reminder_file_leader2)

    time.sleep(60*15)

    i += 1
