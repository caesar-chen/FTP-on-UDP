#!/usr/bin/env python

class SendThread:

    def __init__(self, rxp, filename):
        self.rxp = rxp
        self.filename = filename

    # run a file sending thread
    def run(self, event):
        print 'start postfile'
        try:
            self.rxp.postFile(filename=self.filename, event=event)
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))