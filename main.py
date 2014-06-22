#!/usr/local/bin/python
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

from Freezer import Freezer
from Grinder import Grinder

app = QApplication(sys.argv)

myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')

rawFpga = pandas.read_csv('/Users/minosniu/Dropbox/ShareCadaverDataNI/data_cadaver_0514/rh_gd0_gs0/20140514160633_fpga')
cadGrinder = Grinder(expName='ramp-n-hold', \
                     expDate='20140514', \
                     rawData=rawFpga, \
                     numTrials=10, \
                     gD=0, \
                     gS=0, \
                     analyst="Minos Niu")
cadGrinder.setFreezer(myFreezer)

cadGrinder.show()
app.exec_()
