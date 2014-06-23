import StringIO

__author__ = 'johnrocamora'
import pymongo as mg
import datetime
import pickle
import sys


class Freezer():
    def __init__(self, addr):
        try:
            print addr
            self.client = mg.MongoClient(addr)
            self.db = self.client.cadaverdb
            self.posts = self.db.posts
            self.processed = self.db.processed
            print "Connected to database %s" % addr
        except mg.errors.ConnectionFailure, e:
            print "%s: Could not connect to MongoDB: %s" % (e, addr)


    def freezeTrial(self, expName, expDate, gammaSta, gammaDyn, trialData, analystName):
        s = StringIO.StringIO()
        trialData.to_csv(s)
        serialData = s.getvalue()

        newTrial = {
            "expName": expName,
            "expDate": expDate,
            "analystName": analystName,
            "gammaDyn": gammaDyn,
            "gammaSta": gammaSta,
            "trialData": serialData,
            "isAccepted": True
        }

        try:
            post_id = self.posts.insert(newTrial)
            print post_id
        except mg.errors.ConnectionFailure, e:
            print "%s: Could not connect to MongoDB: %s" % (e, addr)

    def freezeProcessedTrial(self, expName, expDate, gammaSta, gammaDyn, trialData, analystName):
        pickledTrialData = pickle.dumps(trialData)

        newTrial = {
            "expName": expName,
            "expDate": expDate,
            "analystName": analystName,
            "gammaDyn": gammaDyn,
            "gammaSta": gammaSta,
            "trialData": pickledTrialData,
            "isAccepted": True
        }

        try:
            post_id = self.processed.insert(newTrial)
            return post_id
        except mg.errors.ConnectionFailure, e:
            print "%s: Could not connect to MongoDB: %s" % (e, addr)




