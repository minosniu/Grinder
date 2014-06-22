import pickle
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
import pandas

__author__ = 'minosniu'


class Watcher(QMainWindow):
    """"""

    def __init__(self, freezer, parent=None):
        """Constructor for Viewer"""
        self.freezer = freezer

        QMainWindow.__init__(self, parent)
        # self.showMaximized()
        self.createMainFrame()
        # self.drawTrial()

    def queryData(self):
        """Query some data from freezer
        """
        self.allTrials = []
        for post in self.freezer.posts.find({"analyst": "Minos Niu"}):
            self.allTrials.append(pickle.loads(post['trace']))

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
        self.textbox = QLineEdit("Enter num of trials")
        self.textbox.selectAll()
        self.textbox.setMinimumWidth(200)
        # self.connect(self.textbox, SIGNAL('editingFinished ()'), self.onSetNumTrials)

        self.submitButton = QPushButton("&Submit")
        self.connect(self.submitButton, SIGNAL('clicked()'), self.onSubmit)

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

        for w in [self.textbox, self.submitButton, self.grid_cb,
                  slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def onDraw(self):
        self.fig.clear()
        self.fig.hold(True)

        self.ax = self.fig.add_subplot(211)
        self.ax.plot(self.allTrials[0]['musLce0'])

        self.ax = self.fig.add_subplot(212)
        self.ax.plot(self.allTrials[0]['emg0'])
        self.canvas.draw()


    def onSubmit(self):
        self.queryData()
        for trial in self.allTrials:
            print(len(trial['musLce0']))

        self.onDraw()
        # print(self.allTrials[0].musLce0)


def main():
    app = QApplication(sys.argv)

    # myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
    myFreezer = Freezer('mongodb://localhost:27017/')

    cadWatcher = Watcher(myFreezer)

    cadWatcher.show()
    app.exec_()


if __name__ == "__main__":
    main()
