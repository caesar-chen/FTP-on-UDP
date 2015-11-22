#!/usr/bin/env python

import time, threading, sys
from socket import *
from RxP import RxP
from recvthread import RecvThread
from sendthread import SendThread

 #  FxAClient  
 #  deals with the client side command line arguments and supports the following functions:
 #  Connect - to establish connection
 #  Get File(File Name) - download the file from server
 #  Post File (File Name) - upload the file to server
 #  Window (w) - change window size, default window size = 2
 #  Disconnect - close the connection

def main():

    rxpProtocol = None

    # Handling the argument
    arg = sys.argv
    if len(arg) < 3 or len(arg) > 4:
        print 'Invalid command. Please try again.'
        sys.exit()

    #pass the command line arguments
    try:
        clientPort = int(arg[1])
    except ValueError:
        print 'Invalid command. Please try again.'
        sys.exit()

    if not 0 < clientPort < 65536:
        print 'Invalid port number. Please try again.'
        sys.exit()

    #Server IP address
    serverIP = arg[2]

    #netEmu port number
    netEmuPort = int(arg[3])

    #Dest. port number
    desPort = clientPort + 1

    log = "output-client.txt"

    connThread = None
    connStop = threading.Event()
    sThread = None
    sStop = threading.Event()

    #execute user's commend
    while True:
        time.sleep(.500)
        Sinput = raw_input("type connect - to establish connection \n"
                    + "get 'filename' - to download the file from server \n"
                    + "post 'filename' - to upload the file to server \n"
                    + "Window W - to change the window size \n"
                    + "disconnect - to close the connection\n")
        if Sinput.__eq__("connect"):
            rxpProtocol = RxP(serverIP, netEmuPort, clientPort, desPort, log)
            clientProtocol = RecvThread(rxpProtocol)
            connThread = threading.Thread(target=clientProtocol.run, args=(connStop,))
            connThread.start()
            rxpProtocol.connect()
        elif "get" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                rxpProtocol.getFile(s[1])
        elif "post" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                sendThread = SendThread(rxpProtocol, s[1])
                sThread = threading.Thread(target=sendThread.run, args=(sStop,))
                sThread.start()
        elif "window" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split()
                window = int(s[1])
                rxpProtocol.setWindowSize(window)
        elif Sinput.__eq__("disconnect"):
            if rxpProtocol != None:
                rxpProtocol.close()
                connStop.set()
                rxpProtocol.socket.close()

if __name__ == "__main__":
    main()