#!/usr/bin/env python

from rxpHeader import RxPHeader
from rxpTimer import RxPTimer
from rxpWindow import RxPWindow
from socket import *
from collections import deque
import thread


class RxP:
    dataMax = 255

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
        self.rxpWindow = RxPWindow()
        self.rxpTimer = RxPTimer()
        self.transTimer = RxPTimer()
        self.buffer = deque()
        self.output = None
        self.recvFileIndex = 0
        self.threads = []

    def connect(self):
        self.header.cnt = True
        self.header.syn = True
        self.header.seqNum = 0
        self.send(None)
        self.rxpTimer.start()

        while not self.cntBit:
            if self.rxpTimer.isTimeout():
                self.header.syn = True
                self.header.seqNum = 0
                self.send(None)
                self.rxpTimer.start()

        while self.cntBit:
            if self.rxpTimer.isTimeout():
                self.header.syn = False
                self.header.seqNum = 1
                self.send(None)
                self.rxpTimer.start()

        self.header.cnt = False

    def close(self):
        self.header.cnt = True
        self.header.fin = True
        self.header.seqNum = 0
        self.send(None)
        self.rxpTimer.start()

        while self.cntBit == 2:
            if self.rxpTimer.isTimeout():
                self.header.fin = True
                self.header.seqNum = 0
                self.send(None)
                self.rxpTimer.start()

        while self.cntBit == 3:
            if self.rxpTimer.isTimeout():
                self.header.fin = False
                self.header.seqNum = 1
                self.send(None)
                self.rxpTimer.start()

        self.header.cnt = False
        self.reset()

    def listen(self):
        while True:
            recvPacket, address = socket.recvfrom(1024)

            if self.validateChecksum(recvPacket):
                tempHeader = self.getHeader(recvPacket)
                if tempHeader.cnt:
                    self.recvCntPkt(recvPacket)
                elif tempHeader.get:
                    self.recvGetPkt(recvPacket)
                elif tempHeader.post:
                    self.recvPostPkt(recvPacket)
                elif tempHeader.dat:
                    self.recvDataPkt(recvPacket)
            else:
                print 'Received corrupted data, dropped.'

    def reset(self):
        self.rxpWindow = RxPWindow()
        self.rxpTimer = RxPTimer()
        self.cntBit = 0
        self.getBit = 0
        self.postBit = 0
        self.buffer = []
        self.recvFileIndex = 0

    def getFile(self, filename):
        if self.cntBit == 2:
            nameBytes = bytearray(filename)
            self.header.get = True
            self.header.seqNum = 0
            self.send(nameBytes)
            self.header.get = False
            print 'Sending Get initialize msg.'
            self.rxpTimer.start()

            while self.getBit == 0:
                if self.rxpTimer.isTimeout():
                    self.header.get = True
                    self.header.seqNum = 0
                    self.send(nameBytes)
                    self.header.get = False
                    print 'Re-send Get initialize msg.'
                    self.rxpTimer.start()
            print 'Start receiving file.'

        else:
            print 'No connection'

    def send(self, data):
        self.header.ack = False
        datagram = self.pack(self.header.getHeader(), data)
        datagram = self.addChecksum(datagram)
        self.socket.sendto(datagram, (self.serverAddress, self.netEmuPort))

    def sendAck(self):
        self.header.ack = True
        datagram = self.addChecksum(self.header.getHeader())
        self.socket.sendto(datagram, (self.serverAddress, self.netEmuPort))

    def getHeader(self, datagram):
        tmpHeader = RxPHeader()
        tmpHeader.headerFromBytes(datagram)
        return tmpHeader

    def getContent(self, data):
        return data[RxPHeader.headerLen:]

    def pack(self,header, data):
        if data:
            result = header.extend(data)
            return result
        else:
            return header

    def postFile(self, filename):
        if self.cntBit == 2:
            nameBytes = bytearray(filename)
            self.header.post = True
            self.header.seqNum = 0
            self.send(nameBytes)
            self.header.post = False
            print 'Sending Post initialize msg.'
            self.rxpTimer.start()

            while self.postBit == 0:
                if self.rxpTimer.isTimeout():
                    self.header.post = True
                    self.header.seqNum = 0
                    self.send(nameBytes)
                    self.header.post = False
                    print 'Re-send Post initialize msg.'
                    self.rxpTimer.start()

            self.transTimer.start()
            file = open(filename, "rb")
            fileBytes = bytearray(file.read())
            bufferSize = RxP.dataMax - RxPHeader.headerLen
            fileSize = len(fileBytes)
            fileIndex = 0
            self.rxpTimer.start()

            while fileIndex < fileSize or len(self.buffer) > 0:
                if self.rxpTimer.isTimeout():
                    self.rxpWindow.nextToSend = self.rxpWindow.startWindow
                    self.rxpTimer.start()
                    for i in range(len(self.buffer)):
                        if fileIndex >= fileSize:
                            if i == len(self.buffer) - 1:
                                self.header.end = True
                            seq = self.rxpWindow.nextToSend
                            self.header.seqNum = seq
                            self.header.dat = True
                            self.send(self.buffer[i])
                            self.header.dat = False
                            self.header.end = False
                            self.rxpWindow.nextToSend = seq + 1

                if self.rxpWindow.nextToSend <= self.rxpWindow.endWindow and fileIndex < fileSize:
                    data = []
                    if fileIndex + bufferSize > fileSize:
                        data = fileBytes[fileIndex:fileSize]
                    else:
                        data = fileBytes[fileIndex:fileIndex + bufferSize]
                    fileIndex += bufferSize

                if fileIndex >= fileSize:
                    self.header.end = True
                seq = self.rxpWindow.nextToSend
                self.header.seqNum = seq
                self.header.dat = True
                self.send(data)
                self.header.dat = False
                self.header.end = False
                self.rxpWindow.nextToSend = seq + 1
                self.buffer.append(data)

            file.close()
            transTime = self.transTimer.time
            self.postBit = 0
            self.getBit = 0
            self.header.end = False
        else:
            print 'No connection'

    def recvDataPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        if tmpHeader.ack:
            print 'Received Data ACK Num: %d' % tmpHeader.ackNum

            if tmpHeader.ackNum == self.rxpWindow.startWindow:
                self.rxpTimer.start()
                self.rxpWindow.startWindow += 1
                self.rxpWindow.endWindow += 1
                self.buffer.popleft()
        else:
            if self.output == None:
                print 'Output is not ready'
            else:
                if self.recvFileIndex == tmpHeader.seqNum:
                    content = self.getContent(packet)
                    self.output.write(content)
                    self.recvFileIndex += 1

                    if tmpHeader.end:
                        self.output.close()
                        print 'File received'

                seq = tmpHeader.seqNum
                if self.recvFileIndex > seq:
                    self.header.ackNum = seq
                elif self.recvFileIndex <seq:
                    self.header.ackNum = self.recvFileIndex - 1
                self.header.dat = True
                self.sendAck()
                self.header.dat = False

    def recvGetPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if tmpHeader.ack:
            self.getBit = 1
        else:
            if self.getBit == 0:
                content = self.getContent(packet)
                filename = self.bytesToString(content)
                self.getBit = 1
                ###### !!!!
                self.threads.append(thread.start_new_thread(self.postFile(filename)))

    def recvPostPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if tmpHeader.post == 0:
            if tmpHeader.ack:
                self.postBit = 1
            else:
                content = self.getContent(packet)
                filename = self.bytesToString(content)
                self.output = open(filename, "ab")
                self.header.post = True
                self.sendAck()
                self.header.post = False

    def recvCntPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if self.cntBit == 0:
            if tmpHeader.syn:
                print 'Received connection initializing msg [SYN=1]'
                self.header.cnt = True
                self.sendAck()
                self.cntBit = 1
            elif self.header.syn and tmpHeader.ack:
                self.header.syn = False
                self.header.seqNum = 1
                self.send(None)
                print 'Received first SYN ack, sending second msg[SYN=0].'
                self.cntBit = 1
            elif not tmpHeader.fin and not tmpHeader.ack:
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
        elif self.cntBit == 1:
            if not tmpHeader.ack and not tmpHeader.syn:
                self.cntBit = 2
                self.sendAck()
                self.header.cnt = False
                print 'Connection established'
            if not tmpHeader.seqNum and tmpHeader.syn:
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
            if tmpHeader.ack:
                self.cntBit = 2
        elif self.cntBit == 2:
            if tmpHeader.fin:
                print 'Received connection closing msg [FIN=1]'
                self.header.cnt = True
                self.sendAck()
                self.cntBit = 3
            elif self.header.fin and tmpHeader.ack:
                self.header.fin = False
                self.header.seqNum = 1
                self.send(None)
                print 'Received first FIN ack, sending second msg[FIN=0]'
                self.cntBit = 3
            elif not tmpHeader.ack and not tmpHeader.syn:
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
        elif self.cntBit == 3:
            if not tmpHeader.ack and not tmpHeader.fin:
                self.cntBit = 0
                self.sendAck()
                self.header.cnt = False
                self.reset()
                print 'Connection Close'
            elif not tmpHeader.seqNum and tmpHeader.fin:
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
            elif tmpHeader.ack:
                self.cntBit = 0

    def setWindowSize(self, windowSize):
        if self.cntBit == 2:
            self.rxpWindow.windowSize = windowSize
        else:
            print 'Please initialize connection first.'

    def bytesToString(self, data):
        return data.decode("utf-8")




















