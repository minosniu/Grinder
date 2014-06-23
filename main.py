#!/usr/local/bin/python
import pickle
from Freezer import Freezer
import StringIO


myFreezer = Freezer('mongodb://localhost:27017/')

## Provision the Freezer.processed collection
for doc in myFreezer.posts.find():
    myFreezer.processed.insert(doc)

for doc in myFreezer.processed.find():
    myFreezer.processed.update({'_id': doc['_id']},
                               {'$set': {'timeOnset': 0}})
