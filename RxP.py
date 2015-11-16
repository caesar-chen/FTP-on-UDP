#!/usr/bin/env python

import RxPHeader, RxPTimer, random, string, hashlib, thread, logging, cPickle, sys
from socket import *

class RxP:

    def __init__(self, serverAddress, emuPort, hostPort, destPort, filename):
        self.netEmuPort = emuPort
        self.serverAddress = serverAddress
        self.hostPort = hostPort
        self.destPort = destPort
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.header = RxPHeader(hostPort, destPort, 0, 0)
        self.cntBit = 0
        self.getBit = 0
        self.postBit = 0
        self.rxpwindow =
        self.rxpTimer = RxPTimer()


    def connect(self):
        self.header.setCnt(True)
        self.header.setSyn(True)
        self.header.setSeqNum(0)
        self.send(None)
        self.rxpTimer.start()

        while not self.getcntBit():
            if self.rxpTimer.isTimeout():
                self.header.setSyn(True)
                self.header.setSeqNum(0)
                self.send(None)
                self.rxpTimer.start()

        while self.getcntBit():
            if self.rxpTimer.isTimeout():
                self.header.setSyn(False)
                self.header.setSeqNum(1)
                self.send(None)
                self.rxpTimer.start()

        self.header.setCnt(False)
