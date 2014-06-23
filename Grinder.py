from __future__ import print_function

__author__ = "minosniu"

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QTAgg as NavigationToolbar)
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pandas
import matplotlib.pyplot as plt

from Freezer import Freezer


class Grinder(QMainWindow):
    def __init__(self, expName, expDate, rawData, gammaSta, gammaDyn, analystName, parent=None):
        # Metadata into properties
        self.analystName = analystName
        self.expDate = expDate
        self.expName = expName
        self.rawData = rawData
        self.gammaDyn = gammaDyn
        self.gammaSta = gammaSta

        # Some useful stuff
        self.allEndLines = []
        self.iBegins = []
        self.iEnds = []
        self.currEndLine = None
        self.currEndLineId = None
        self.baseChannel = 'musLce0'
        self.isDragging = False

        QMainWindow.__init__(self, parent)
        # self.showMaximized()
        self.createMainFrame()
        self.setNumTrials()

    def createMainFrame(self):
        self.main_frame = QWidget()

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.canvas.mpl_connect('key_press_event', self.onKey)
        self.canvas.mpl_connect('pick_event', self.onPick)
        self.canvas.mpl_connect('button_press_event', self.onMouseDown)
        self.canvas.mpl_connect('button_release_event', self.onMouseUp)
        self.canvas.mpl_connect('motion_notify_event', self.onMouseMotion)


        # Initial draw
        self.fig.clear()
        self.fig.hold(True)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.rawData[self.baseChannel])

        # Other GUI controls
        #
        self.numTrialBox = QSpinBox()
        self.numTrialBox.setMinimum(1)
        self.numTrialBox.setValue(2)
        self.numTrialBox.setMinimumWidth(200)
        self.connect(self.numTrialBox, SIGNAL('valueChanged(int)'), self.onNumTrialBox)

        self.submitButton = QPushButton("&Submit")
        self.connect(self.submitButton, SIGNAL('clicked()'), self.onSubmit)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.onGrid)

        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.onSlider)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [self.numTrialBox, self.submitButton, self.grid_cb,
                  slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def setEndLine(self, new_x):
        minLen = 50
        if self.currEndLineId > 0:
            leftx, lefty = self.allEndLines[self.currEndLineId - 1].get_data()
            lbound = leftx[0] + minLen
        else:
            lbound = minLen

        if self.currEndLineId < self.numTrials - 1:
            rightx, righty = self.allEndLines[self.currEndLineId + 1].get_data()
            rbound = rightx[0] - minLen
        else:
            rbound = len(self.rawData) - minLen

        xs, ys = self.currEndLine.get_data()
        new_xs = [min(rbound, max(lbound, new_x)) for xx in xs]
        self.currEndLine.set_data(new_xs, ys)
        self.canvas.draw()

    # IOC for all trials
    def setNumTrials(self, n=2):
        for eachLine in self.allEndLines:
            self.ax.lines.remove(eachLine)

        self.numTrials = n
        self.allEndLines = []

        maxL = 100
        initialIndex = 0  # was 100
        length = (self.rawData.shape[0] - initialIndex) / self.numTrials

        self.iBegins = [initialIndex + i * length for i in xrange(self.numTrials)]
        self.iEnds = [initialIndex + (i + 1) * length - 1 for i in xrange(self.numTrials)]

        for i in xrange(self.numTrials):
            self.allEndLines.append(self.ax.axvline(self.iEnds[i], 0, maxL, color='k', picker=10))

        self.beginLine = self.ax.axvline(0, 0, maxL, color='r', linewidth=5)

        # Select the first line by default
        self.setCurrEndLine(self.allEndLines[0])

        self.canvas.draw()

    def setAllTrials(self):
        self.iEnds = [int(l.get_data()[0][0]) for l in self.allEndLines]
        for i in xrange(self.numTrials - 1):
            self.iBegins[i + 1] = self.iEnds[i] + 1
        self.allTraces = [self.rawData[self.iBegins[i] : self.iEnds[i]] for i in xrange(self.numTrials)]

    def freezeAllTrials(self):
        try:
            for eachTrial in self.allTraces:
                self.freezer.sendToFreezer(expName=self.expName,
                                           expDate=self.expDate,
                                           gammaDyn=self.gammaDyn,
                                           gammaSta=self.gammaSta,
                                           trialData=eachTrial,
                                           analystName=self.analystName)
        except:
            print("Error when writing to database")
        finally:
            print("Successfully froze %d trials." % self.numTrials)

    def setFreezer(self, someFreezer):
        self.freezer = someFreezer

    def setCurrEndLine(self, artist):
        self.currEndLine = artist
        for i, line in enumerate(self.allEndLines):
            if line == self.currEndLine:
                self.currEndLineId = i
                line.set_color('r')
            else:
                line.set_color('k')

    def onMouseDown(self, event):
        self.isDragging = True

    def onMouseUp(self, event):
        self.isDragging = False

    def onMouseMotion(self, event):
        if self.isDragging:
            self.setEndLine(event.xdata)

    def onGrid(self):
        pass

    def onSlider(self):
        pass

    def onNumTrialBox(self, value):
        """Update how many trials the analyst sees
        """
        self.setNumTrials(value)

    def onSubmit(self):
        # Split trials into memory based on user input
        self.setAllTrials()

        # Save trials to Freezer (MongoDB database)
        self.freezeAllTrials()
        self.close()

    def onPick(self, event):
        self.setCurrEndLine(event.artist)
        self.canvas.draw()

    def onKey(self, event):
        if event.key in '[':
            xs, ys = self.currEndLine.get_data()
            new_xs = [xx - 20 for xx in xs]
            self.currEndLine.set_data(new_xs, ys)
        elif event.key in ']':
            xs, ys = self.currEndLine.get_data()
            new_xs = [xx + 20 for xx in xs]
            self.currEndLine.set_data(new_xs, ys)
        elif event.key in '{':
            xs, ys = self.currEndLine.get_data()
            new_xs = [xx - 100 for xx in xs]
            self.currEndLine.set_data(new_xs, ys)
        elif event.key in '}':
            xs, ys = self.currEndLine.get_data()
            new_xs = [xx + 100 for xx in xs]
            self.currEndLine.set_data(new_xs, ys)
        self.canvas.draw()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
    myFreezer = Freezer('mongodb://localhost:27017/')

    gd = int(sys.argv[1])
    gs = int(sys.argv[2])
    filename = sys.argv[3]

    rawData = pandas.read_csv(filename)
    cadGrinder = Grinder(expName='ramp-n-hold',
                         expDate='20140514',
                         rawData=rawData,
                         gammaDyn=gd,
                         gammaSta=gs,
                         analystName="Minos Niu")
    cadGrinder.setFreezer(myFreezer)

    cadGrinder.show()
    app.exec_()
