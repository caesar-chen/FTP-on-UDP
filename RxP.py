#!/usr/bin/env python

from rxpHeader import RxPHeader
from rxpTimer import RxPTimer
from rxpWindow import RxPWindow
from threads import SendThread
from socket import *
from collections import deque
from crc import crc16xmodem
import unicodedata, sys


class RxP:
    dataMax = 255 # max data in the packet

    # refer to rxpHeader class for more info
    def __init__(self, hostAddress, emuPort, hostPort, destPort, filename):
        self.netEmuPort = emuPort
        self.hostAddress = hostAddress
        self.hostPort = hostPort
        self.destPort = destPort
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.hostAddress, self.hostPort))
        self.header = RxPHeader(hostPort, destPort, 0, 0)
        self.cntBit = 0 # stands for connection state(3 way handshake)
        self.getBit = 0 # get file 
        self.postBit = 0 #post file
        self.rxpWindow = RxPWindow()
        self.rxpTimer = RxPTimer()
        self.transTimer = RxPTimer()
        self.buffer = deque() # buffer to store data
        self.output = None # output file
        self.recvFileIndex = 0 # current index of receiving file
        self.threads = [] # supports multiple clients

    #  When user type in "connect" command Establish handshake connection with
    #  host by sending SYN messages. Handling the time out situation 
    #  cntBit = 0 : listening for connection 
    #  cntBit = 1 : received first SYN = 1 packet
    def connect(self):
        print 'start to connect'
        self.header.cnt = True
        self.header.syn = True
        self.header.seqNum = 0
        self.send(None)
        self.rxpTimer.start()
        print 'Send first msg[SYN=1].'

        while self.cntBit == 0:
            if self.rxpTimer.isTimeout():
                self.header.syn = True
                self.header.seqNum = 0
                self.send(None)
                print 'Re-Send first msg[SYN=1].'
                self.rxpTimer.start()

        while self.cntBit == 1:
            if self.rxpTimer.isTimeout():
                self.header.syn = False
                self.header.seqNum = 1
                self.send(None)
                print 'Re-Send first msg[SYN=0].'
                self.rxpTimer.start()

        self.header.cnt = False

    #  When receive "disconnect" command,it will close connection. 
    #  cntBit = 2 : connection established. 
    #  cntBit = 3 : closing wait
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
                print 'Re-Send first msg[FIN=1]'
                self.rxpTimer.start()

        while self.cntBit == 3:
            if self.rxpTimer.isTimeout():
                self.header.fin = False
                self.header.seqNum = 1
                self.send(None)
                print 'Re-Send first msg[FIN=0]'
                self.rxpTimer.start()

        self.header.cnt = False
        print 'Connection Closed'
        self.reset()

     # Listening the incoming request including connect request, get, post, and
     # data action by checking the received packet contents
    def listen(self, event):
        print 'start to listen'
        while True and not event.stopped():
            self.socket.settimeout(1)
            try:
                recvPacket, address = self.socket.recvfrom(1024)
            except IOError:
                continue
            packet = bytearray(recvPacket)

            if self.validateChecksum(packet):
                tempHeader = self.getHeader(packet)
                if tempHeader.cnt:
                    print 'control packet'
                    self.recvCntPkt(packet)
                elif tempHeader.get:
                    print 'get packet'
                    self.recvGetPkt(packet)
                elif tempHeader.post:
                    print 'post packet'
                    self.recvPostPkt(packet)
                elif tempHeader.dat:
                    print 'data packet'
                    self.recvDataPkt(packet)
            else:
                print 'Received corrupted data, dropped.'

    # reset all setting
    def reset(self):
        self.rxpWindow = RxPWindow()
        self.rxpTimer = RxPTimer()
        self.cntBit = 0
        self.getBit = 0
        self.postBit = 0
        self.buffer = deque()
        self.recvFileIndex = 0
        self.output = None

    #  client uses getFile method to get a file from server side protocol sends
    #  the requested file to client side
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

    # Protocol send incoming data into Datagrams through UDP socket the data
    # need to be add check sum before sending
    def send(self, data):
        print 'sending seq#: %d' % self.header.seqNum
        self.header.ack = False
        datagram = self.pack(self.header.getHeader(), data)
        datagram = self.addChecksum(datagram)
        self.socket.sendto(datagram, (self.hostAddress, self.netEmuPort))

    # Getting header's ack number and add check sum to this ack number then
    # send new ACK through UDP socket
    def sendAck(self):
        print 'acking num: %d' %self.header.ackNum
        self.header.ack = True
        datagram = self.addChecksum(self.header.getHeader())
        self.socket.sendto(datagram, (self.hostAddress, self.netEmuPort))

    # Getting the header information from received data
    def getHeader(self, datagram):
        tmpHeader = RxPHeader()
        tmpHeader.headerFromBytes(datagram)
        return tmpHeader

    # Getting the actual content from received data
    def getContent(self, data):
        return data[RxPHeader.headerLen:]

     # Packing header array and data array into a new array, so that we can send
     # this new data to the UDP socket
    def pack(self,header, data):
        if data:
            result = header + data
            return result
        else:
            return header

    # Sending file to the server.
    def postFile(self, filename, event):
        if self.cntBit == 2:
            nameBytes = bytearray(filename)
            self.header.post = True
            self.header.seqNum = 0
            self.send(nameBytes)
            self.header.post = False
            print 'Sending Post initialize msg.'
            self.rxpTimer.start()

            while self.postBit == 0 and not event.stopped():
                if self.rxpTimer.isTimeout():
                    self.header.post = True
                    self.header.seqNum = 0
                    self.send(nameBytes)
                    self.header.post = False
                    print 'Re-send Post initialize msg.'
                    self.rxpTimer.start()
            if event.stopped():
                print 'Post file interrupted'
                return

            self.transTimer.start()
            file = open(filename, "rb")
            fileBytes = bytearray(file.read())
            bufferSize = RxP.dataMax - RxPHeader.headerLen
            fileSize = len(fileBytes)
            fileIndex = 0
            self.rxpTimer.start()

            while (fileIndex < fileSize or len(self.buffer) > 0) and not event.stopped():
                if self.rxpTimer.isTimeout():
                    self.rxpWindow.nextToSend = self.rxpWindow.startWindow
                    self.rxpTimer.start()
                    for i in range(len(self.buffer)):
                        if fileIndex >= fileSize:
                            if i == len(self.buffer) - 1:
                                print 'set end of file'
                                self.header.end = True
                        seq = self.rxpWindow.nextToSend
                        self.header.seqNum = seq
                        self.header.dat = True
                        try:
                            self.send(self.buffer[i])
                        except:
                            print ("Corruption or Reodring rate too high, connection fails")
                            sys.exit()
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
            print 'postbit set to 0, getbit set to 0'
            self.postBit = 0
            self.getBit = 0
            self.header.end = False

            if event.stopped():
                print 'Post file interrupted'
        else:
            print 'No connection'

    # Handle received data transmission packet.
    def recvDataPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        if tmpHeader.ack:
            print 'Received Data ACK Num: %d' % tmpHeader.ackNum

            if tmpHeader.ackNum == self.rxpWindow.startWindow:
                print 'moving window'
                self.rxpTimer.start()
                self.rxpWindow.startWindow += 1
                self.rxpWindow.endWindow += 1
                print 'poping buffer'
                self.buffer.popleft()
        else:
            if self.output == None:
                print 'Output is not ready'
            else:
                if self.recvFileIndex == tmpHeader.seqNum:
                    content = self.getContent(packet)
                    self.output.write(content)
                    self.recvFileIndex += 1
                    self.output.flush()

                    if tmpHeader.end:
                        self.output.close()
                        print 'File received'

                seq = tmpHeader.seqNum
                if self.recvFileIndex > seq:
                    self.header.ackNum = seq
                elif self.recvFileIndex < seq:
                    if self.recvFileIndex != 0:
                        self.header.ackNum = self.recvFileIndex - 1
                    else:
                        self.header.ackNum = 0
                self.header.dat = True
                self.sendAck()
                self.header.dat = False

    # Handle get file packet
    def recvGetPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if tmpHeader.ack:
            self.getBit = 1
        else:
            if self.getBit == 0:
                content = self.getContent(packet)
                uniFilename = self.bytesToString(content)
                filename = unicodedata.normalize('NFKD', uniFilename).encode('utf-8','ignore')
                self.getBit = 1
                sendTread = SendThread(self, filename)
                self.threads.append(sendTread)
                sendTread.start()
            self.header.get = True
            self.sendAck()
            self.header.get = False

    # Handle post file packet
    def recvPostPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if self.postBit == 0:
            if tmpHeader.ack:
                print 'postbit set to 1'
                self.postBit = 1
            else:
                content = self.getContent(packet)
                filename = self.bytesToString(content)
                self.output = open("./down/" + filename, "ab")
                self.header.post = True
                print 'sending post ack'
                self.sendAck()
                self.header.post = False

    # receive connection establishment packet
    # 3 way handshake
    # closing wait
    def recvCntPkt(self, packet):
        tmpHeader = self.getHeader(packet)
        seq = tmpHeader.seqNum
        self.header.ackNum = seq

        if self.cntBit == 0:
            if tmpHeader.syn:
                print 'Received connection initializing msg [SYN=1]'
                self.header.cnt = True
                self.sendAck()
                print 'cntbit set to 1'
                self.cntBit = 1
            elif self.header.syn and tmpHeader.ack:
                self.header.syn = False
                self.header.seqNum = 1
                self.send(None)
                print 'Received first SYN ack, sending second msg[SYN=0]. cnt bit set to 1'
                self.cntBit = 1
            elif not tmpHeader.fin and not tmpHeader.ack:
                print 'server received SYN from client, and sent back ACK to client'
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
        elif self.cntBit == 1:
            if not tmpHeader.ack and not tmpHeader.syn:
                print 'cntbit set to 22222'
                self.cntBit = 2
                self.sendAck()
                self.header.cnt = False
                print 'Connection established'
            if tmpHeader.seqNum == 0 and tmpHeader.syn:
                print 'Second SYN initialization'
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
            if tmpHeader.ack:
                print 'cntbit set to 2'
                self.cntBit = 2
        elif self.cntBit == 2:
            if tmpHeader.fin:
                print 'Received connection closing msg [FIN=1] cntbit set to 3'
                self.header.cnt = True
                self.sendAck()
                self.cntBit = 3
            elif self.header.fin and tmpHeader.ack:
                self.header.fin = False
                self.header.seqNum = 1
                self.send(None)
                print 'Received first FIN ack, sending second msg[FIN=0] cnt bit set to 3'
                self.cntBit = 3
            elif not tmpHeader.ack and not tmpHeader.syn:
                self.header.cnt = True
                self.sendAck()
                self.header.cnt = False
        elif self.cntBit == 3:
            if not tmpHeader.ack and not tmpHeader.fin:
                print 'cnt bit set to 000000'
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
                print 'cnt bit set to 0'
                self.cntBit = 0

    # set the window size for protocol
    def setWindowSize(self, windowSize):
        if self.cntBit == 2:
            self.rxpWindow.windowSize = windowSize
        else:
            print 'Please initialize connection first.'

    # Convert the ASCII byte[] data into String
    def bytesToString(self, data):
        return data.decode('utf-8')

     # Before sending the packet, we have to add a check sum field into each
     # packet to make sure the correction of data
    def addChecksum(self, packet):
        data = ''
        packet[14] = 0
        packet[15] = 0
        for byte in packet:
            data += str(byte)
        checksum = crc16xmodem(data)
        packet[14] = checksum >> 8
        packet[15] = checksum & 0xFF
        return packet

    # Using this check sum function to check every received packet's corruption
    def validateChecksum(self, packet):
        correct = False
        data = ''
        firstB = packet[14]
        secondB = packet[15]
        packet[14] = 0
        packet[15] = 0
        for byte in packet:
            data += str(byte)
        checksum = crc16xmodem(data)
        msb = checksum >> 8
        lsb = checksum & 0xFF
        if msb == firstB and lsb == secondB:
            correct = True
        return correct
