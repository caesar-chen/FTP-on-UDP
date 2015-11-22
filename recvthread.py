#!/usr/bin/env python

class RecvThread:

    def __init__(self, rxp):
        self.rxp = rxp

    #not sure what exception listen() will have
    def run(self, event):
        try:
            print 'start to run'
            self.rxp.listen(event=event)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))