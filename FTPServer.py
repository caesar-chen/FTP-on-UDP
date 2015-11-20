#!/usr/bin/env python

import sys, hashlib, logging, cPickle, time, thread
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

    rxpProtocol = RxP(serverIP, netEmuPort, hostPort, desPort, log)

    serverProtocol = RecvThread(rxpProtocol)
    thread.start_new_thread(serverProtocol.run(), ())

    #execute user's commend
    #可以改 "argument"
    while (True):
        Sinput = input("type Window W - to change the window size \n"
                    + "terminate - to terminate the server")

        if "window" in Sinput:
            s = Sinput.split("\\s")
            wsize = (int)s[1]
            rxpProtocol.setWindowSize(wsize)
        else if Sinput.__eq__("terminate"):
            rxpProtocol.close()
            #close serverProtocol
            #for t in rxpProtocol.getThreadList():
                #need discuss
                #close t
            rxpProtocol.getSocket().close()
            print ("Server is closed")
            break


if __name__ == "__main__":
    main()