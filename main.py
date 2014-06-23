#!/usr/local/bin/python
import pickle
from Freezer import Freezer
import StringIO


myFreezer = Freezer('mongodb://localhost:27017/')

# for doc in myFreezer.posts.find():
    # myFreezer.posts.update({'_id': doc['_id']},
    #                        {'$set': {'trialDataPlain': data}})

for doc in myFreezer.processed.find():
    myFreezer.processed.update({'_id': doc['_id']},
                           {'$set': {'timeOnset': 0}})
