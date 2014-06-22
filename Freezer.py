__author__ = 'johnrocamora'
import pymongo as mg
import datetime
import pickle
import sys

class Freezer():
    def __init__(self, addr):
        try:
            self.client = mg.MongoClient(addr)
            self.db = self.client.johndb
            self.posts = self.db.posts
            print "Connected successfully!!!"
        except mg.errors.ConnectionFailure, e:
            print "%s: Could not connect to MongoDB: %s" % (e, addr)


    def sendToFreezer(self, expName, expDate, gammaSta, gammaDyn, trialData, analystName):
        pickledTrialData = pickle.dumps(trialData)

        newTrial={
            "expName" : expName,
            "expDate" : expDate,
            "analystName" : analystName,
            "gammaDyn" : gammaDyn,
            "gammaSta" : gammaSta,
            "trialData" : pickledTrialData,
            "isAccepted" : True
        }

        post_id = self.posts.insert(newTrial)

        print "Saving doc with _id: ", post_id

        sys.stdout.flush()





