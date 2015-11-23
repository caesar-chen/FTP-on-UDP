#!/usr/bin/env python

# window class for flow control
# deal with window related function
# changing window size
# set start window, end window
class RxPWindow:

    def __init__(self):
        self.windowSize = 2
        self.startWindow = 0
        self.endWindow = self.windowSize - 1
        self.nextToSend = 0
