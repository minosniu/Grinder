#!/usr/local/bin/python
from __future__ import print_function

import sys

from PyQt4.QtGui import *
import pandas

from Freezer import Freezer
from Grinder import Grinder

app = QApplication(sys.argv)

# myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
myFreezer = Freezer('mongodb://localhost:27017/')

# rawFpga = pandas.read_csv('/Users/minosniu/Dropbox/ShareCadaverDataNI/data_cadaver_0514/rh_gd0_gs0/20140514160633_fpga')

rawFpga = pandas.read_csv('/Users/minosniu/Dropbox/ShareCadaverDataNI/data_cadaver_0514/rh_gd100_gs100/20140514161044_fpga')
cadGrinder = Grinder(expName='ramp-n-hold', \
                     expDate='20140514', \
                     rawData=rawFpga, \
                     numTrials=10, \
                     gD=100, \
                     gS=100, \
                     analyst="Minos Niu")
cadGrinder.setFreezer(myFreezer)

cadGrinder.show()
app.exec_()
