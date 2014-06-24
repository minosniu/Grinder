__author__ = 'minosniu'
import sys
import os

path_root = '/Users/minosniu/Dropbox/ShareCadaverDataNI/data_cadaver_0514/rh_'

expt = 'ramp-n-hold'
date = '20140514'
analyst = 'Minos Niu'
addr = 'mongodb://localhost:27017/'

if __name__ == '__main__':
    for gd in [0, 100, 200]:
        for gs in [0, 100, 200]:
    # for gd in [0]:
    #     for gs in [0]:
            path = path_root + 'gd%d_gs%d' % (gd, gs)
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for f in files:
                fullname = os.path.abspath(os.path.join(path, f))
                print('Processing gd_%d gs_%d' % (gd, gs))
                os.system('python Grinder.py "%s" "%s" "%s" %d %d "%s" "%s"' %
                          (expt, date, fullname, gd, gs, analyst, addr))

