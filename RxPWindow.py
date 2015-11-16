#!/usr/bin/env python

class RxPWindow:

    def __init__(self):
        self.windowSize = 5
        self.startWindow = 0
        self.endWindow = self.windowSize - 1
        self.nextToSend = 0


    def setNextToSend(self, next):
        self.nextToSend = next


    def setWindowSize(self, size):
        self.windowSize = size


    def setStartWindow(self, s):
        self.startWindow = s


    def setEndWindow(self, e):
        self.endWindow = e
