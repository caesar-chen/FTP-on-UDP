#!/usr/bin/env python

import random, string, hashlib, thread, logging, cPickle, sys
from socket import *

class RxP:

    def __init__(self, serverAddress, emuPort, hostPort, destPort, filename):
        self.netEmuPort = emuPort
        self.serverAddress = serverAddress
        self.hostPort = hostPort
        self.destPort = destPort
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.header =
        self.cntBit = 0
        self.getBit = 0
        self.postBit = 0
        self.rxpwindow =


    def connect(self):
        header.setCnt()