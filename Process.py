import StringIO
from Freezer import Freezer
import pandas as pd
from pylab import plot, figure, show, subplot

__author__ = 'minosniu'

def queryData(queryStr):
    """Query some data from freezer
    """
    allTrials = []
    allDocs = myFreezer.posts.find(eval(queryStr))
    allIDs = []
    for doc in allDocs:
        s = StringIO.StringIO(doc['trialData'])
        t = pd.read_csv(s)
        allTrials.append(t)
        allIDs.append(doc['_id'])
    return allTrials, allIDs

def findOnset(currTrial, baseCh = 'musLce0'):
    """Add the field 'onset' to all documents"""
    l = currTrial[baseCh][0:100]
    base = sum(l) / float(len(l))
    th = base * 1.02
    f = lambda i: currTrial.musLce0[i] <= th <= currTrial.musLce0[min(len(currTrial) - 1, i + 1)]

    possible = filter(f, range(len(currTrial.musLce0)))
    if possible:
        currOnset = possible[0]
    else:
        currOnset = len(currTrial) / 2

    return currOnset

queryStr = """{"analystName": "Minos Niu", "expName": "ramp-n-hold", "gammaDyn": 200, "gammaSta": 200} """
allAlignedTrials = []
allOnsets = []

addr = 'mongodb://localhost:27017/'
myFreezer = Freezer(addr)
allColl = myFreezer.db.collection_names()

if not 'after' in allColl:
    myFreezer.db.create_collection('after')

### Query trials based on queryStr
allTrials, allIDs = queryData(queryStr)
numTrials = len(allTrials)
allOnsets = [0 for i in xrange(numTrials)]

print "Found", numTrials, "trials."

### Find trial onsets, default based on musLce0
for i, trial in enumerate(allTrials):
    allOnsets[i] = findOnset(trial)
    print("Trial %d has onset %d" % (i, allOnsets[i]))
    allAlignedTrials.append(trial.drop(xrange(allOnsets[i] - 100)).reset_index())

### Unify the length of all trials
uniLen = min(map(len, allAlignedTrials))
for i, trial in enumerate(allAlignedTrials):
    allAlignedTrials[i] = allAlignedTrials[i][:uniLen]

print(map(len, allAlignedTrials))

figure()
ax = subplot(111)
ax.set_ylim([-8, 8])

for trial in allAlignedTrials:
    plot(trial.emg0)
show()
