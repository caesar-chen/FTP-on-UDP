#!/usr/bin/env python

# header class for RxP
class RxPHeader:
    headerLen = 16 # header length

    def __init__(self, sourcePort=-1, destPort=-1, seqNum=0, ackNum=0):
        self.sourcePort = sourcePort # The port number of the packet source
        self.destPort = destPort # The port number of the packet destination
        self.seqNum = seqNum # Current sequence number
        self.ackNum = ackNum # Current ack number
        self.ack = False # bit to indicate package is ack package
        self.end = False # bit to indicate if the package is the last package
        self.dat = False # bit to indicate if the package is data package
        self.cnt = False # bit to indicate if the package contains connection data
        self.syn = False # bit to initiate a connection
        self.fin = False # bit to close a connection
        self.get = False # bit for get file request
        self.post = False # bit for post file request
        self.checksum = 0 # Checksum field
        self.header = bytearray(16) # Byte array of header for sending

    # convert all instance variables of RxP header into byte array
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
        self.header[12] = RxPHeader.headerLen & 0xFF
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
    
    # given a byte array, convert it into a RxPHeader
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
        return self.setHeader()

    def setHeaderFromBytes(self, header):
        self.header = header
