#!/usr/bin/env python

import threading

class SendThread(threading.Thread):

    def __init__(self, rxp, filename):
        super(SendThread, self).__init__()
        self.rxp = rxp
        self.filename = filename
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        try:
            self.rxp.postFile(self.filename, self)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))