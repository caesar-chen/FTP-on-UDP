#!/usr/bin/env python

import sys
from socket import *
from RxP import RxP
from threads import RecvThread

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
    # validate
    if not 0 < hostPort < 65536:
        print 'Invalid port number. Please try again.'
        sys.exit()

    #Server IP address
    serverIP = arg[2]
    # validate
    if not _validIP(serverIP):
        print 'IP address is not valid, please try again'
        sys.exit()

    # netEmu port number
    try:
        netEmuPort = int(arg[3])
    except ValueError:
        print 'Invalid command. Please try again.'
        sys.exit()
    # validate
    if not 0 < netEmuPort < 65536:
        print 'Invalid port number. Please try again.'
        sys.exit()

    # Dest. port number
    desPort = hostPort - 1

    rxpProtocol = RxP(serverIP, netEmuPort, hostPort, desPort, log)
    serverProtocol = RecvThread(rxpProtocol)
    serverProtocol.start()

    # execute user's commend
    while (True):
        Sinput = raw_input("type Window W - to change the window size \n"
                    + "terminate - to terminate the server\n")
        if "window" in Sinput:
            s = Sinput.split()
            try:
                wsize = int(s[1])
            except ValueError:
                print 'Invalid window size. Please try again.'
                sys.exit()
            if not 0 < wsize < 50:
                print 'Window size too big. Please try again.'
                sys.exit()
            print "Set window size to " + str(wsize)
            rxpProtocol.setWindowSize(wsize)
        # close server
        elif Sinput.__eq__("terminate"):
            rxpProtocol.close()
            serverProtocol.stop()
            for thread in rxpProtocol.threads:
                thread.stop()
            print ("Server is closed")
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