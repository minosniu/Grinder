import matplotlib
#matplotlib.use('TkAgg')
matplotlib.use('Qt4Agg')
from matplotlib.widgets import Button
import pandas
from pylab import ginput
import matplotlib.pyplot as plt
from Freezer import Freezer
# unit test later

def getYValueLimits(rawData, baseChannel):
    numElements = rawData.shape[0]

    minX = 0;
    maxX = numElements - 1

    dataY = [rawData[baseChannel][i] for i in \
             xrange(numElements)]

    minY = min(dataY)
    maxY = max(dataY)

    # 3minIdY =

    return [minY, maxY]


class Grinder():
    def __init__(self, expName, expDate, rawData, numTrials, gS, gD):
        self.expDate = expDate
        self.expName = expName
        self.rawData = rawData
        self.numTrials = numTrials
        self.gD = gD
        self.gS = gS

        self.fig, self.ax = plt.subplots()
        self.currArtist = self.ax

        self.endlines = []
        self.iBegins = []
        self.iEnds = []


    def setNumTrials(self):
        self.numTrials = int(raw_input('How many trials do you see?'))

    def onButton(self, event):
        self.iEnds = [l.get_data()[0][0] for l in self.endlines]
        for i in xrange(self.numTrials - 1):
            self.iBegins[i+1] = self.iEnds[i] + 1

        # Rewrite this line as a return from the button
        #+++ Verify with subplot
        self.allTraces = [[self.rawData[self.baseChannel][self.iBegins[i]:self.iEnds[i]]] \
                     for i in xrange(self.numTrials)]


        print("Trial Num:", len(self.allTraces))

        for eachTrial in self.allTraces:
            self.freezer.sendToFreezer(expName = self.expName, \
                                  expDate = self.expDate, \
                                  gD = self.gD,\
                                  gS = self.gS, \
                                  trialData = eachTrial)

    def onPick(self, event):
        self.currArtist = event.artist
        for line in self.endlines:
            if (line == self.currArtist):
                line.set_color('r')
            else:
                line.set_color('k')
        self.fig.canvas.draw()

    def onKey(self, event):
        if event.key in '[':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx - 2 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in ']':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx + 2 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in '{':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx - 20 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in '}':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx + 20 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        self.fig.canvas.draw()

    def splitTrial(self, baseChannel):
        self.baseChannel = baseChannel

        self.ax.plot(self.rawData[self.baseChannel])
        numElements = self.rawData.shape[0]

        self.ax1 = plt.axes([0.0, 0.5, 0.1, 0.075])
        self.b1 = Button(self.ax1, 'Submit')
        self.b1.on_clicked(self.onButton)

        begin = ginput(1)
        end = ginput(1)

        length = int(end[0][0] - begin[0][0])

        self.iBegins = [int(begin[0][0]) + i * length for i in xrange(self.numTrials)]
        self.iEnds = [int(begin[0][0]) + (i + 1) * length - 1 for i in xrange(self.numTrials)]



        [minL, maxL] = getYValueLimits(self.rawData, self.baseChannel)
        for iLine in xrange(self.numTrials):
            self.endlines.append(self.ax.axvline(self.iEnds[iLine], 0, maxL, color='k', picker=5))
            self.fig.canvas.mpl_connect('pick_event', self.onPick)
            self.fig.canvas.mpl_connect('key_press_event', self.onKey)

        self.fig.canvas.draw()

    def setFreezer(self, someFreezer):
        self.freezer = someFreezer



if __name__ == '__main__':
    myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
    rawFpga = pandas.read_csv('fpga')
    cad_grinder = Grinder(expName = 'ramp-n-hold',\
                          expDate = '20140514',\
                          rawData = rawFpga,\
                          numTrials = 10,\
                          gD = 0,\
                          gS = 0)
    cad_grinder.setFreezer(myFreezer)
    cad_grinder.splitTrial('musLce0')
    raw_input("<Hit enter to close")
    plt.close(cad_grinder.fig)

