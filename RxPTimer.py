#!/usr/bin/env python

from time import time

class RxPTimer:

    def __init__(self):
        self.time = 0
        self.timeout = 1


    def start(self):
        self.time = time()


    def getTime(self):
        return self.time - time()


    def isTimeout(self):
        if time() - self.time < self.timeout:
            return False
        else:
            return True
