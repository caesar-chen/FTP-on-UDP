#!/usr/bin/env python

import time

class RxPTimer:

    def __init__(self):
        self.time = 0
        self.timeout = 1


    def start(self):
        self.time = time.time()


    def getTime(self):
        return self.time - time.time()


    def isTimeout(self):
        if time.time() - self.time < self.timeout:
            return False
        else:
            return True
