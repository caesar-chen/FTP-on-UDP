Wenqi Hu: 
Shizhe Chen: schen381@gatech.edu
CS3251 Section A prj2
Nov 24/2015

Names and descriptions of all files submitted:
crc.py: crc library for checksum
FTPClient.py: client initialization file
FTPServer.py: server initialization file
RxP.py: most important file. All detailed implementation of protocol inside
rxpHeader.py: define the header for RxP protocol
rxpTimer: RxP Timer class, deal with time out issues
rxpWindow: window class for flow control, deal with window related function
threads.py: handle multiple clients
protocol.pdf: updated protocol and API description with sufficient detail

Detailed instructions for compiling and running your client and server programs:
python FTPServer.py 8081 127.0.0.1 5000
type:
"window": set the window size
"terminate": close server
python FTPServer.py 8080 127.0.0.1 5000
type:
"connect": connect to server
"get": get file form server
"post": post file to server
"window": set the window size
"disconnect": close connection

Your updated protocol and API description with sufficient detail:
see protocol.pdf

Any known bugs, limitations of your design or program:
Our program handles each possible error. Should works great.
One thing need to notice, the ¡°get¡±ed or ¡°post¡±ed files located in down folder.