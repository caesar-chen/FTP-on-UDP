#!/usr/bin/env python

class RxPWindow:

    def __init__(self):
        self.windowSize = 5
        self.startWindow = 0
        self.endWindow = self.windowSize - 1
        self.nextToSend = 0
