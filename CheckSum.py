from crc import crc16xmodem

def addChecksum(self, packet):
    data = ''
    for byte in packet[0:14]:
        data += str(byte)
    checksum = crc16xmodem(data)
    packet[14] = checksum >> 8
    packet[15] = checksum & 0xFF
    return packet

def validateChecksum(self, packet):
    correct = False
    data = ''
    for byte in packet[0:14]:
        data += str(byte)
    checksum = crc16xmodem(data)
    msb = checksum >> 8
    lsb = checksum & 0xFF
    if msb == packet[14] and lsb == packet[15]:
        correct = True
    return correct


##
##下面是我的测试， 你可以看看
##

# def addChecksum(packet):
#     data = ''
#     for byte in packet[0:14]:
#         data += str(byte)
#     checksum = crc16xmodem(data)
#     print checksum
#     packet[14] = checksum >> 8
#     packet[15] = checksum & 0xFF
#     print packet
#     print packet[14]
#     print packet[15]
#     return packet

# def validateChecksum(packet):
#     print 'checksum result'
#     print packet[0:14]
#     correct = False
#     data = ''
#     for byte in packet[0:14]:
#         data += str(byte)
#     checksum = crc16xmodem(data)
#     print checksum

#     msb = checksum >> 8
#     lsb = checksum & 0xFF
#     if msb == packet[14] and lsb == packet[15]:
#         correct = True
#     print correct
#     #return correct

# a = bytearray()
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")
# a.append("h")

# b = addChecksum(a)

# c = bytearray()
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append("h")
# c.append(145)
# c.append(200)
# validateChecksum(c)


