#!/usr/bin/env python

import sys, threading
from socket import *
from RxP import RxP
from recvthread import RecvThread
from sendthread import SendThread

 #  FxAServer
 #  deals with the server side command line arguments and supports the following functions:
 #  start server
 #  Window (w) - change window size, default window size = 2
 #  terminate - terminate the server

def main():

    print ("Server Starts")

    # Handling the argument
    arg = sys.argv
    if len(arg) < 3 or len(arg) > 4:
        print 'Invalid command. Please try again.'
        sys.exit()

    log = "output-server.txt"

    #pass the command line arguments
    try:
        hostPort = int(arg[1])
    except ValueError:
        print 'Invalid command. Please try again.'
        sys.exit()

    if not 0 < hostPort < 65536:
        print 'Invalid port number. Please try again.'
        sys.exit()

    #Server IP address
    serverIP = arg[2]

    #netEmu port number
    netEmuPort = int(arg[3])

    #Dest. port number
    desPort = hostPort - 1

    # rxpProtocol = RxP(serverIP, netEmuPort, hostPort, desPort, log)
    # serverStop = threading.Event()
    # serverProtocol = RecvThread(rxpProtocol)
    # sTread = threading.Thread(target=serverProtocol.run, args=(serverStop,))
    # sTread.start()

    rxpProtocol = RxP(serverIP, netEmuPort, hostPort, desPort, log)
    serverProtocol = RecvThread(rxpProtocol)
    serverProtocol.start()

    #execute user's commend
    while (True):
        Sinput = raw_input("type Window W - to change the window size \n"
                    + "terminate - to terminate the server\n")
        if "window" in Sinput:
            s = Sinput.split()
            wsize = int(s[1])
            rxpProtocol.setWindowSize(wsize)
        # close server
        elif Sinput.__eq__("terminate"):
            rxpProtocol.close()
            serverProtocol.stop()
            for thread in rxpProtocol.threads:
                thread.stop()
            print ("Server is closed")
            break


if __name__ == "__main__":
    main()