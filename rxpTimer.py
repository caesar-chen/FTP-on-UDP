#!/usr/bin/env python

from time import time

class RxPTimer:
    timeout = 100

    def __init__(self):
        self.time = 0


    def start(self):
        self.time = time()


    def getTime(self):
        return self.time - time()


    def isTimeout(self):
        if time() - self.time < RxPTimer.timeout:
            return False
        else:
            return True
