#!/usr/bin/env python

import threading


class RecvThread(threading.Thread):

    def __init__(self, rxp):
        super(RecvThread, self).__init__()
        self.rxp = rxp
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()
        print self._stop.isSet()

    def stopped(self):
        return self._stop.isSet()

    # run a thread to listen incoming data
    def run(self):
        self.rxp.listen(self)


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

    # run a file sending thread
    def run(self):
        self.rxp.postFile(self.filename, self)
