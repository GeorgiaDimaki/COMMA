# -*- coding: utf-8 -*-

# from pymongo import *
# import pymongo
import json

# def connectToDB(db_name):
#
#     try:
#         client = MongoClient()
#         print 'Connected successfully!'
#     except pymongo.errors.ConnectionFailure, e:
#         "An error occured while connecting to database"
#         return None, None
#
#     db = client[db_name]
#     return client, db
#
# '''
# exports the documents from database <db_name> collection <collection_name> that match the specified query
# in a .json file specified in <filename>
# '''
# def export_db(filename, db_name, collection_name, query=None):
#
#     client, db = connectToDB(db_name)
#
#     # this code clears the previous file. only needed when we export db in the same file
#     with open(filename, 'w') as data:
#         data.write('')
#
#     for t in db[collection_name].find(query):
#         with open(filename, 'a') as data:
#             data.write(json.dumps(t, ensure_ascii=False).encode('utf-8'))
#             data.write("\n")
#
#     client.close()
#
# '''
# imports the contents of a .json file <filename> in a mongodb database <db_name> and collection <collection_name>
# '''
#
# def import_db(filename, db_name, collection_name):
#
#     client, db = connectToDB(db_name)
#
#     with open(filename, 'r') as data:
#         for line in data.readlines():
#             db[collection_name].insert(json.loads(line.decode('utf-8')))
#
#     client.close()

'''
imports the contents of a .json file <filename> in a memory array.
'''
def import_db_to_memory(filename):

    db = []
    with open(filename, 'r') as data:
        for line in data.readlines():
            db.append(json.loads(line.decode('utf-8')))

    return db
