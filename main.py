#!/usr/local/bin/python
import pickle
from Freezer import Freezer


myFreezer = Freezer('mongodb://localhost:27017/')

# for doc in myFreezer.posts.find():
#     t = pickle.loads(doc['trialData'])
#     t = t.reset_index()
#     myFreezer.posts.update({'_id': doc['_id']},
#                            {'$set': {'trialData': pickle.dumps(t)}})

for doc in myFreezer.processed.find():
    myFreezer.processed.update({'_id': doc['_id']},
                           {'$set': {'timeOnset': 0}})
