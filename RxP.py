#!/usr/bin/env python

from rxpHeader import RxPHeader
from rxpTimer import RxPTimer
from rxpWindow import RxPWindow
from socket import *
from collections import deque
import string, thread, logging, sys


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
            file = open(filename, "rb")
            fileBytes = bytearray(file.read())
            self.header.get = True
            self.header.seqNum = 0
            self.send(fileBytes)
            self.header.get = False
            print 'Sending Post initialize msg.'
            self.rxpTimer.start()

            while self.postBit == 0:
                if self.rxpTimer.isTimeout():
                    self.header.get = True
                    self.header.seqNum = 0
                    self.send(fileBytes)
                    self.header.get = False
                    print 'Re-send Post initialize msg.'
                    self.rxpTimer.start()

            self.transTimer.start()
            fileSize = 0
            bufferSize = RxP.dataMax - RxPHeader.headerLen
            self.rxpTimer.start()

            while
                if self.rxpTimer.isTimeout():
                    self.rxpWindow.nextToSend = self.rxpWindow.startWindow
                    self.rxpTimer.start()
                    ############# need fixing

                    for data in self.buffer:
                        # if end then...
                        self.header.end = True

                        seq = self.rxpWindow.nextToSend
                        self.header.seqNum = seq
                        self.header.dat = True
                        self.send(data)
                        self.header.dat = False
                        self.header.end = False
                        self.rxpWindow.nextToSend = seq + 1

                ############## need fixing
                if self.rxpWindow.nextToSend <= self.rxpWindow.endWindow && something:
                    fileSize += bufferSize
                    ##### need fixing

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

    def setWindowSize(self, windowSize):
        if self.cntBit == 2:
            self.rxpWindow.windowSize = windowSize
        else:
            print 'Please initialize connection first.'

    def bytesToString(self, data):
        return data.decode("utf-8")




    def addChecksum(self, packet, bits = 8):
        crc = 0xFFFF
        res = packet.decode("utf-8")
        for op, code in zip(res[0::2], res[1::2]):
            crc = crc ^ int(op + code, 16)
            for bit in range(0 , bits):
                if (crc & 0x0001)  == 0x0001:
                    crc = ((crc >> 1) ^ 0xA001)
                else:
                    crc = crc >> 1
        msb = crc >> 8
        lsb = crc & 0x00FF
        packet.append(msb)
        packet.append(lsb)
        return packet

    def validateChecksum(self, packet, bits = 8):
        bool correct = False
        crc = 0xFFFF
        res = packet.decode("utf-8")
        for op, code in zip(res[0::2], res[1::2]):
            crc = crc ^ int(op + code, 16)
            for bit in range(0 , bits):
                if (crc & 0x0001)  == 0x0001:
                    crc = ((crc >> 1) ^ 0xA001)
                else:
                    crc = crc >> 1
        msb = crc >> 8
        lsb = crc & 0x00FF
        if msb == packet[14] and lsb == packet[15]:
            correct = True
        return correct















