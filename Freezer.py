__author__ = 'johnrocamora'
import pandas as pd
from pymongo import MongoClient
from pylab import *
import datetime
import pickle
import sys

class Freezer():
    def __init__(self, addr):
        self.client = MongoClient(addr)
        self.db = self.client.johndb
        self.posts = self.db.posts

        #self.collection = self.db.testCollection


    def sendToFreezer(self, expName, expDate, gS, gD, trialData):
        pickledTrialData = pickle.dumps(trialData)

        newTrial={
            "expt" : expName,
            "date" : expDate,
            "gamma_s" : gS,
            "gamma_d" : gD,
            "trace" : pickledTrialData,
            "is_accepted" : True
        }

        post_id = self.posts.insert(newTrial)

        print "Saving doc with _id: ", post_id

        sys.stdout.flush()





