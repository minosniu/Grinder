import matplotlib
matplotlib.use('TkAgg')
from matplotlib.widgets import Button
import pandas
from pylab import ginput
import matplotlib.pyplot as plt
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
    def __init__(self, rawData):
        self.fig, self.ax = plt.subplots()
        self.currArtist = self.ax

        self.endlines = []

        self.rawData = rawData

    def onButton(self, event):
        print [l.get_data() for l in self.endlines]

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


    def splitTrial(self, numTrials, baseChannel):
        self.ax.plot(self.rawData[baseChannel])
        numElements = self.rawData.shape[0]

        self.ax1 = plt.axes([0.0, 0.5, 0.1, 0.075])
        self.b1 = Button(self.ax1, 'Submit')
        self.b1.on_clicked(self.onButton)


        begin = ginput(1)
        end = ginput(1)

        length = int(end[0][0] - begin[0][0])

        iBegins = [int(begin[0][0]) + i * length for i in xrange(numTrials)]
        iEnds = [int(begin[0][0]) + (i + 1) * length - 1 for i in xrange(numTrials)]
        print(iEnds)

        allTraces = [[self.rawData[baseChannel][iBegins[i]:iEnds[i]]] \
                     for i in xrange(i)]

        [minL, maxL] = getYValueLimits(self.rawData, baseChannel)
        for iLine in xrange(numTrials):
            self.endlines.append(self.ax.axvline(iEnds[iLine], 0, maxL, color='k', picker=5))
            self.fig.canvas.mpl_connect('pick_event', self.onPick)
            self.fig.canvas.mpl_connect('key_press_event', self.onKey)

        self.fig.canvas.draw()

        return allTraces


if __name__ == '__main__':
    rawFpga = pandas.read_csv('fpga')
    cad_grinder = Grinder(rawFpga)
    results = cad_grinder.splitTrial(10, 'musLce0')
    print results[0]
    print len(results)
    raw_input("<Hit enter to close")
    plt.close(cad_grinder.fig)

