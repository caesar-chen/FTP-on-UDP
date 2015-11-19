#!/usr/bin/env python

import sys, hashlib, logging, cPickle, time, thread
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

    clientProtocol = None
    sendThread = None
    log = "output-client.txt"

    #execute user's commend
    #可以改
    while (True):
        time.sleep(.500)
        Sinput = input("type connect - to establish connection \n"
                    + "get 'filename' - to download the file from server \n"
                    + "post 'filename' - to upload the file to server \n"
                    + "Window W - to change the window size \n"
                    + "disconnect - to close the connection")
        if Sinput.__eq__("connect"):
            rxpProtocol = RxP(serverIP, netEmuPort, clientPort, desPort, log)
            clientProtocol = RecvThread(rxpProtocol)

            #need discuss
            #是不是把recvthread里面的method放进来
            #thread.start_new_thread(_handler, (connectionSocket, addr))
            #clientProtocol.start()

            rxpProtocol.connect()
        else if "get" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split("\\s")
                rxpProtocol.getFile(s[1])
        else if "post" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split("\\s")
                sendThread = SendThread(rxpProtocol, s[1])

                #need discuss
                #是不是把recvthread里面的method放进来
                #thread.start_new_thread(_handler, (connectionSocket, addr))
                #clientProtocol.start()
        else if "window" in Sinput:
            if rxpProtocol != None:
                s = Sinput.split("\\s")
                window = int(s[1])
                rxpProtocol.setWindowSize(window)
        else if Sinput.__eq__("disconnect"):
            if rxpProtocol != None:
                rxpProtocol.close()

                #need discuss
                ##stop clientProtocol

                if sendThread != None:
                    #need discuss
                    ##stop sendThread
                rxpProtocol.getSocket().close()


if __name__ == "__main__":
    main()