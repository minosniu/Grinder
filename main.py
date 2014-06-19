#!/usr/local/bin/python
import pandas
from Freezer import Freezer
from Grinder import Grinder

myFreezer = Freezer('mongodb://diophantus.usc.edu:27017/')
rawFpga = pandas.read_csv('fpga')
cad_grinder = Grinder(expName = 'ramp-n-hold', \
                      expDate = '20140514', \
                      rawData = rawFpga, \
                      numTrials = 10, \
                      gD = 0, \
                      gS = 0)
cad_grinder.setFreezer(myFreezer)
cad_grinder.splitTrial('musLce0')
raw_input("<Hit enter to close")
