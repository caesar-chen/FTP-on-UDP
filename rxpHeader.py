#!/usr/bin/env python

class RxPHeader:
    headerLen = 16

    def __init__(self, sourcePort, destPort, seqNum, ackNum):
        self.sourcePort = sourcePort
        self.destPort = destPort
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.ack = False
        self.end = False
        self.dat = False
        self.cnt = False
        self.syn = False
        self.fin = False
        self.get = False
        self.post = False
        self.checksum = 0
        self.header = bytearray([])


    def setHeader(self):
        self.header[0] = self.sourcePort >> 8
        self.header[1] = self.sourcePort & 0xFF
        self.header[2] = self.destPort >> 8
        self.header[3] = self.destPort & 0xFF
        self.header[4] = self.seqNum >> 24
        self.header[5] = self.seqNum >> 16
        self.header[6] = self.seqNum >> 8
        self.header[7] = self.seqNum & 0xFF
        self.header[8] = self.ackNum >> 24
        self.header[9] = self.ackNum >> 16
        self.header[10] = self.ackNum >> 8
        self.header[11] = self.ackNum & 0xFF
        self.header[12] = RxPHeader.headerLen
        self.header[13] = 0

        if self.fin:
            self.header[13] = self.header[13] | 0x1
        if self.syn:
            self.header[13] = self.header[13] | 0x2
        if self.cnt:
            self.header[13] = self.header[13] | 0x4
        if self.dat:
            self.header[13] = self.header[13] | 0x8
        if self.ack:
            self.header[13] = self.header[13] | 0x10
        if self.end:
            self.header[13] = self.header[13] | 0x20
        if self.get:
            self.header[13] = self.header[13] | 0x40
        if self.post:
            self.header[13] = self.header[13] | 0x80

        self.header[14] = self.checksum >> 8
        self.header[15] = self.checksum & 0xFF

        return self.header

    def headerFromBytes(self, header):
        self.sourcePort = (self.header[0] << 8 | (0 | 0xFF)) & self.header[1]
        self.destPort = (self.header[2] << 8 | (0 | 0xFF)) & self.header[3]
        self.seqNum = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | (0 | 0xFF) & self.header[7]
        self.ackNum = self.header[8] << 24 | self.header[9] << 16 | self.header[10] << 8 | (0 | 0xFF) & self.header[11]

        if (self.header[13] & 0x1) == 0x1:
            self.fin = True
        if (self.header[13] & 0x2) == 0x2:
            self.syn = True
        if (self.header[13] & 0x4) == 0x4:
            self.cnt = True
        if (self.header[13] & 0x8) == 0x8:
            self.dat = True
        if (self.header[13] & 0x10) == 0x10:
            self.ack = True
        if (self.header[13] & 0x20) == 0x20:
            self.end = True
        if (self.header[13] & 0x40) == 0x40:
            self.get = True
        if (self.header[13] & 0x80) == 0x80:
            self.post = True
        self.checksum = self.header[14] << 8 | (0 | 0xFF) & self.header[15]


    def getHeader(self):
        self.setHeader()
        return self.header


    def setHeaderFromBytes(self, header):
        self.header = header


    def getSourcePort(self):
        return self.sourcePort


    def setSourcePort(self, srcPort):
        self.sourcePort = srcPort


    def getDestPort(self):
        return self.destPort


    def setDestPort(self, destPort):
        self.destPort = destPort


    def getSeqNum(self):
        return self.seqNum


    def setSeqNum(self, seqNum):
        self.seqNum = seqNum


    def getAckNum(self):
        return self.ackNum


    def setAckNum(self, ackNum):
        self.ackNum = ackNum


    def isDat(self):
        return self.dat


    def setDat(self, dat):
        self.dat = dat


    def isAck(self):
        return self.ack


    def setAck(self, ack):
        self.ack = ack


    def isEnd(self):
        return self.end


    def setEnd(self, end):
        self.end = end


    def isCnt(self):
        return self.cnt


    def setCnt(self, cnt):
        self.cnt = cnt


    def isSyn(self):
        return self.syn


    def setSyn(self, syn):
        self.syn = syn


    def isFin(self):
        return self.fin


    def setFin(self, fin):
        self.fin = fin


    def isGet(self):
        return self.get


    def setGet(self, get):
        self.get = get


    def isPost(self):
        return self.post


    def setPost(self, post):
        self.post = post


    def getChecksum(self):
        return self.checksum


    def setChecksum(self, checksum):
        self.checksum = checksum
