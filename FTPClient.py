#!/usr/bin/env python

import time, sys
from socket import *
from RxP import RxP
from threads import RecvThread, SendThread

# FxAClient
# deals with the client side command line arguments and supports:
# Connect - to establish connection
# Get File(File Name) - download the file from server
# Post File (File Name) - upload the file to server
# Window (size) - change window size, default window size = 2
# Disconnect - close the connection

def main():

    rxpProtocol = None

    # Handling the argument
    arg = sys.argv
    if len(arg) < 3 or len(arg) > 4:
        print 'Invalid command. Please try again.'
        sys.exit()

    # pass the command line arguments
    try:
        clientPort = int(arg[1])
    except ValueError:
        print 'Invalid command. Please try again.'
        sys.exit()

    if not 0 < clientPort < 65536:
        print 'Invalid port number. Please try again.'
        sys.exit()

    # Server IP address
    serverIP = arg[2]

    if not _validIP(serverIP):
        print 'IP address is not valid, please try again'
        sys.exit()

    # netEmu port number
    netEmuPort = int(arg[3])

    # Dest. port number
    desPort = clientPort + 1

    log = "output-client.txt"

    clientProtocol = None
    sendThread = None

    connThread = None
    sThread = None

    #execute user's commend
    while True:
        time.sleep(.500)
        Sinput = raw_input("type connect - to establish connection \n"
                    + "get 'filename' - to download the file from server \n"
                    + "post 'filename' - to upload the file to server \n"
                    + "Window W - to change the window size \n"
                    + "disconnect - to close the connection\n"
                    + 'quit - to quit the application\n')
        if Sinput.__eq__("connect"):
            rxpProtocol = RxP(serverIP, netEmuPort, clientPort, desPort, log)
            clientProtocol = RecvThread(rxpProtocol)
            clientProtocol.start()
            rxpProtocol.connect()
        # get file form server
        elif "get" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                rxpProtocol.getFile(s[1])
        # post file form server
        elif "post" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                sendThread = SendThread(rxpProtocol, s[1])
                sendThread.start()
        # set the window size
        elif "window" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                window = int(s[1])
                rxpProtocol.setWindowSize(window)
        #close connection
        elif Sinput.__eq__("disconnect"):
            if rxpProtocol != None:
                rxpProtocol.close()
                clientProtocol.stop()
                rxpProtocol.socket.close()
                rxpProtocol = None
        elif Sinput.__eq__("quit"):
            if rxpProtocol:
                print 'disconnect before quit'
            else:
                break


# check IP format validation
def _validIP(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for num in parts:
        try:
            part = int(num)
        except ValueError:
            print 'Invalid IP. Please try again.'
            sys.exit()
        if not 0 <= part <= 255:
            return False
    return True


if __name__ == "__main__":
    main()