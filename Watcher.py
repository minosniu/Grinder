import StringIO
from pymongo import MongoClient

import sys
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QTAgg as NavigationToolbar)
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Freezer import Freezer
import pandas as pd

__author__ = 'minosniu'


class Watcher(QMainWindow):
    """"""

    def __init__(self, freezer, parent=None):
        """Constructor for Viewer"""
        self.freezer = freezer
        self.numTrials = 0
        self.currTrialId = 0
        self.allTrials = None
        self.allAlignedTrials = None
        self.allOnsets = None

        # # Useful stuff
        self.onsetLine1 = None
        self.onsetLine2 = None

        QMainWindow.__init__(self, parent)
        # self.showMaximized()
        self.createMainFrame()
        # self.drawTrial()

    def queryData(self, queryStr):
        """Query some data from freezer
        """
        self.allTrials = []
        self.allAlignedTrials = []
        self.allOnsets = []
        self.queryStr = queryStr

        # allDocs = self.freezer.processed.find(eval(self.queryStr))
        allDocs = self.freezer.posts.find(eval(self.queryStr))
        for doc in allDocs:
            s = StringIO.StringIO(doc['trialData'])
            t = pd.read_csv(s)
            self.allTrials.append(t)

            t = 0#doc['timeOnset']
            self.allOnsets.append(t)

        self.numTrials = len(self.allTrials)

        # self.allAlignedTrials = [t for t in self.allTrials]
        print "Found", self.numTrials, "trials."

    def freezeAllOnsets(self):
        """Freeze timeOnset field in Freezer
        """
        allDocs = self.freezer.processed.find(eval(self.queryStr))
        try:
            for onset, doc in zip(self.allOnsets, allDocs):
                self.freezer.processed.update({'_id': doc['_id']},
                                              {'$set': {'timeOnset': onset}})
            print("Froze %d onsets" % len(self.allOnsets))
        except:
            print("Error updating")

    def createMainFrame(self):
        self.main_frame = QWidget()

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.textbox = QTextEdit("""{"analystName": "Minos Niu",
                                     "gammaDyn": 100,
                                     "gammaSta": 100}
                                 """)
        self.textbox.selectAll()
        self.textbox.setMinimumWidth(200)

        self.queryButton = QPushButton("&Query")
        self.connect(self.queryButton, SIGNAL('clicked()'), self.onSubmit)

        self.fwdButton = QPushButton("&>>")
        self.connect(self.fwdButton, SIGNAL('clicked()'), self.onFwd)

        self.bwdButton = QPushButton("&<<")
        self.connect(self.bwdButton, SIGNAL('clicked()'), self.onBwd)

        self.alignButton = QPushButton("&Close")
        self.connect(self.alignButton, SIGNAL('clicked()'), self.onFinish)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        # self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.onGrid)

        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        # self.connect(self.slider, SIGNAL('valueChanged(int)'), self.onSlider)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [self.textbox, self.queryButton,
                  self.bwdButton, self.fwdButton, self.alignButton,
                  self.grid_cb, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def drawCurrTrial(self):
        self.fig.clear()
        self.fig.hold(True)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.ax1.plot(self.currTrial['musLce0'])
        self.ax1.set_ylim([0.5, 1.5])
        self.ax2.plot(self.currTrial['emg0'])
        self.ax2.set_ylim([-6.0, 6.0])
        self.canvas.draw()

    def setOnsetLine(self):
        maxL = 100

        if self.onsetLine1 in self.ax1.lines:
            self.ax1.lines.remove(self.onsetLine1)
        if self.onsetLine2 in self.ax2.lines:
            self.ax2.lines.remove(self.onsetLine2)

        self.onsetLine1 = self.ax1.axvline(self.currOnset, 0, maxL, color='r')
        self.onsetLine2 = self.ax2.axvline(self.currOnset, 0, maxL, color='r')
        self.canvas.draw()

    def setOnset(self):
        """Add the field 'onset' to all documents"""
        l = self.currTrial.musLce0[0:100]
        base = sum(l) / float(len(l))
        th = base * 1.02
        f = lambda i: self.currTrial.musLce0[i] <= th <= self.currTrial.musLce0[min(len(self.currTrial) - 1, i + 1)]

        possible = filter(f, range(len(self.currTrial.musLce0)))
        if possible:
            self.currOnset = possible[0]
        else:
            self.currOnset = len(self.currTrial) / 2
        self.allOnsets[self.currTrialId] = self.currOnset
        self.allAlignedTrials[self.currTrialId] = self.currTrial.drop(xrange(self.currOnset - 100))

    def setCurrTrial(self, n=0):
        self.currTrialId = n
        # print(len(self.allTrials))
        self.currTrial = self.allTrials[self.currTrialId]
        # print(self.currTrialId, len(self.currTrial))

    def onFwd(self):
        """Go forward 1 trial"""
        self.setCurrTrial(min(self.currTrialId + 1, self.numTrials - 1))
        self.drawCurrTrial()
        # self.setOnset()
        # self.setOnsetLine()

    def onBwd(self):
        """Go backward 1 trial"""
        self.setCurrTrial(max(self.currTrialId - 1, 0))
        self.drawCurrTrial()
        # self.setOnset()
        # self.setOnsetLine()

    def onFinish(self):
        # self.freezeAllOnsets()
        self.close()

    def onSubmit(self):
        self.queryData(str(self.textbox.toPlainText()))
        self.setCurrTrial()
        self.drawCurrTrial()
        # self.setOnset()
        # self.setOnsetLine()


def main():
    app = QApplication(sys.argv)

    # myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
    myFreezer = Freezer('mongodb://localhost:27017/')

    cadWatcher = Watcher(myFreezer)

    cadWatcher.show()
    app.exec_()


if __name__ == "__main__":
    main()
