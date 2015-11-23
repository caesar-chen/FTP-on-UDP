#!/usr/bin/env python

from time import time

# RxP Timer class, deal with time out issues
class RxPTimer:
    timeout = 0.5

    def __init__(self):
        self.time = 0


    def start(self):
        self.time = time()

#   calculate the time difference between current time
#   and the time when timer starts, in seconds
    def getTime(self):
        return self.time - time()

#   Checks if timeout occurs
    def isTimeout(self):
        if time() - self.time < RxPTimer.timeout:
            return False
        else:
            return True
