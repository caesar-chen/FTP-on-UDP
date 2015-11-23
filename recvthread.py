#!/usr/bin/env python

import threading

class RecvThread(threading.Thread):

    def __init__(self, rxp):
        super(RecvThread, self).__init__()
        self.rxp = rxp
        self._stop = threading.Event()

    def stop(self):
        print 'stop called'
        self._stop.set()
        print self._stop.isSet()

    def stopped(self):
        return self._stop.isSet()

    #not sure what exception listen() will have
    def run(self):
        try:
            print 'start to run'
            self.rxp.listen(self)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))