#!/usr/bin/env python

class RxPHeader:
    headerLen = 16

    def __init__(self, sourcePort=-1, destPort=-1, seqNum=-1, ackNum=-1):
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
        self.header = bytearray()


    def setHeader(self):
        self.header.append(self.sourcePort >> 8)
        self.header.append(self.sourcePort & 0xFF)
        self.header.append(self.destPort >> 8)
        self.header.append(self.destPort & 0xFF)
        self.header.append(self.seqNum >> 24)
        self.header.append(self.seqNum >> 16)
        self.header.append(self.seqNum >> 8)
        self.header.append(self.seqNum & 0xFF)
        self.header.append(self.ackNum >> 24)
        self.header.append(self.ackNum >> 16)
        self.header.append(self.ackNum >> 8)
        self.header.append(self.ackNum & 0xFF)
        self.header.append(RxPHeader.headerLen)
        self.header.append(0)

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

        self.header.append(self.checksum >> 8)
        self.header.append(self.checksum & 0xFF)

        return self.header

    def headerFromBytes(self, header):
        self.sourcePort = (header[0] << 8 | (0 | 0xFF)) & header[1]
        self.destPort = (header[2] << 8 | (0 | 0xFF)) & header[3]
        self.seqNum = header[4] << 24 | header[5] << 16 | header[6] << 8 | (0 | 0xFF) & header[7]
        self.ackNum = header[8] << 24 | header[9] << 16 | header[10] << 8 | (0 | 0xFF) & header[11]

        if header[13] & 0x1 == 0x1:
            self.fin = True
        if header[13] & 0x2 == 0x2:
            self.syn = True
        if header[13] & 0x4 == 0x4:
            self.cnt = True
        if header[13] & 0x8 == 0x8:
            self.dat = True
        if header[13] & 0x10 == 0x10:
            self.ack = True
        if header[13] & 0x20 == 0x20:
            self.end = True
        if header[13] & 0x40 == 0x40:
            self.get = True
        if header[13] & 0x80 == 0x80:
            self.post = True
        self.checksum = header[14] << 8 | (0 | 0xFF) & header[15]

    def getHeader(self):
        self.setHeader()
        return self.header

    def setHeaderFromBytes(self, header):
        self.header = header

    def setSourcePort(self, srcPort):
        self.sourcePort = srcPort

    def setDestPort(self, destPort):
        self.destPort = destPort

    def setSeqNum(self, seqNum):
        self.seqNum = seqNum

    def setAckNum(self, ackNum):
        self.ackNum = ackNum

    def setDat(self, dat):
        self.dat = dat

    def setAck(self, ack):
        self.ack = ack

    def setEnd(self, end):
        self.end = end

    def setCnt(self, cnt):
        self.cnt = cnt

    def setSyn(self, syn):
        self.syn = syn


    def setFin(self, fin):
        self.fin = fin

    def setGet(self, get):
        self.get = get

    def setPost(self, post):
        self.post = post

    def setChecksum(self, checksum):
        self.checksum = checksum
