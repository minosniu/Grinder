from __future__ import print_function

import sys

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


class Grinder(QMainWindow):
    def __init__(self, expName, expDate, rawData, numTrials, gS, gD, parent=None):
        # Metadata into properties
        self.expDate = expDate
        self.expName = expName
        self.rawData = rawData
        self.numTrials = numTrials
        self.gD = gD
        self.gS = gS

        # Some useful stuff
        self.endlines = []
        self.iBegins = []
        self.iEnds = []
        self.currArtist = None
        self.baseChannel = 'musLce0'

        QMainWindow.__init__(self, parent)
        self.showMaximized()
        self.create_main_frame()
        self.drawTrial()

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.fig = Figure((5.0, 4.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.canvas.mpl_connect('key_press_event', self.onKey)
        self.canvas.mpl_connect('pick_event', self.onPick)

        # Other GUI controls
        #
        self.textbox = QLineEdit("Enter num of trials")
        self.textbox.selectAll()
        self.textbox.setMinimumWidth(200)
        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.onSetNumTrials)

        self.submitButton = QPushButton("&Submit")
        self.connect(self.submitButton, SIGNAL('clicked()'), self.onSubmit)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)

        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [  self.textbox, self.submitButton, self.grid_cb,
                    slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def onSetNumTrials(self):
        pass

    def onSubmit(self):
        self.iEnds = [l.get_data()[0][0] for l in self.endlines]
        for i in xrange(self.numTrials - 1):
            self.iBegins[i+1] = self.iEnds[i] + 1

        # Rewrite this line as a return from the button
        #+++ Verify with subplot
        self.allTraces = [[self.rawData[self.baseChannel][self.iBegins[i]:self.iEnds[i]]] \
                          for i in xrange(self.numTrials)]


        print("Total trials:", len(self.allTraces))

        # Save to Freezer (MongoDB database)
        for eachTrial in self.allTraces:
            self.freezer.sendToFreezer(expName = self.expName, \
                                       expDate = self.expDate, \
                                       gD = self.gD, \
                                       gS = self.gS, \
                                       trialData = eachTrial)


    def onPick(self, event):
        self.currArtist = event.artist
        for line in self.endlines:
            if (line == self.currArtist):
                line.set_color('r')
            else:
                line.set_color('k')
        self.canvas.draw()

    def onKey(self, event):
        if event.key in '[':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx - 20 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in ']':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx + 20 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in '{':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx - 100 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        elif event.key in '}':
            xs, ys = self.currArtist.get_data()
            new_xs = [xx + 100 for xx in xs]
            self.currArtist.set_data(new_xs, ys)
        self.canvas.draw()

    def on_draw(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.axes.imshow(self.data, interpolation='nearest')
        #self.axes.plot([1,2,3])
        self.canvas.draw()

    def drawTrial(self):
        self.fig.clear()
        self.fig.hold(True)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(self.rawData[self.baseChannel])
        self.canvas.draw()

        begin = [[1000, 0]]
        end = [[1400, 0]]

        length = int(end[0][0] - begin[0][0])

        self.iBegins = [int(begin[0][0]) + i * length for i in xrange(self.numTrials)]
        self.iEnds = [int(begin[0][0]) + (i + 1) * length - 1 for i in xrange(self.numTrials)]

        maxL = 100

        for iLine in xrange(self.numTrials):
            self.endlines.append(self.ax.axvline(self.iEnds[iLine], 0, maxL, color='k', picker=5))


    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.canvas, self.mpl_toolbar)


def main():
    app = QApplication(sys.argv)

    rawFpga = pandas.read_csv('fpga')
    cadGrinder = Grinder(expName='ramp-n-hold', \
                         expDate='20140514', \
                         rawData=rawFpga, \
                         numTrials=10, \
                         gD=0, \
                         gS=0)
    cadGrinder.show()
    app.exec_()


if __name__ == "__main__":
    main()
