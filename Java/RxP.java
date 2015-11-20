import java.io.BufferedOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.ArrayList;

public class RxP {
    public static final int BUFFERMAX = 255;
    private DatagramSocket socket;
    private RxPHeader header;
    private InetAddress serverAddress;
    private DatagramPacket sendPacket;
    private DatagramPacket recvPacket;
    private RxPWindow rxpWindow;
    private RxPTimer rxpTimer;

    private int cntBit;
    private int getBit;
    private int postBit;
    private int netEmuPort;
    private int hostPort;
    private int destPort;

    private RxPTimer transTimer;
    private ArrayList<SendThread> threadList;
    QueueBuffer<byte[]> queueBuffer;
    private int recvFileIndex;

    BufferedOutputStream outBuffer;
    FileOutputStream fileOut;

    /**
     * Default Constructor of RxP class, setting up basic variables
     */
    public RxP() {
        this.netEmuPort = -1;
        this.hostPort = -1;
        this.setDestPort(-1);
        this.serverAddress = null;
        socket = null;
        header = null;
        sendPacket = null;
        recvPacket = null;
        cntBit = 0;
        getBit = 0;
        postBit = 0;
        rxpWindow = new RxPWindow();
        rxpTimer = new RxPTimer();
        queueBuffer = new QueueBuffer<byte[]>();
        recvPacket = new DatagramPacket(new byte[BUFFERMAX], BUFFERMAX);
        transTimer = new RxPTimer();
    }

    /**
     * Constructing the RxP class with corresponding input variables including
     * serverAddress, netEmuport, hostPort, destPort and filename
     * 
     * @throws IOException
     */
    public RxP(InetAddress serverAddress, int emuPort, int hostPort,
            int destPort, String filename) throws IOException {
        this.serverAddress = serverAddress;
        this.netEmuPort = emuPort;
        this.hostPort = hostPort;
        this.destPort = destPort;
        socket = new DatagramSocket(hostPort);
        header = new RxPHeader((short) hostPort, (short) destPort, 0, 0);
        cntBit = 0;
        getBit = 0;
        postBit = 0;
        rxpWindow = new RxPWindow();
        rxpTimer = new RxPTimer();
        queueBuffer = new QueueBuffer<byte[]>();
        recvPacket = new DatagramPacket(new byte[BUFFERMAX], BUFFERMAX);
        transTimer = new RxPTimer();
        threadList = new ArrayList<SendThread>();
    }


    /**
     * Reinitializing all the basic attributes with default value recreating
     * window, timer, queueBuffer, recvPacket, recvFileIndex setting cntBit,
     * getFlag, postFlag to 0
     */
    public void init() {
        rxpWindow = new RxPWindow();
        rxpTimer = new RxPTimer();
        cntBit = 0;
        getBit = 0;
        postBit = 0;
        queueBuffer = new QueueBuffer<byte[]>();
        recvPacket = new DatagramPacket(new byte[BUFFERMAX], BUFFERMAX);
        recvFileIndex = 0;
    }

    /**
     * When user type in "connect" command Establish handshake connection with
     * host by sending SYN messages. Handling the time out situation 
     * cntBit : connection flag 
     * cntBit = 0 : listening for connection cntBit = 1 :
     * received first SYN = 1 packet.
     */
    public void connect() throws IOException {
        header.setCnt(true);

        /* Sending initial msg SYN = 1 */
        header.setSyn(true);
        header.setSeqNum(0);
        this.send(null);
        rxpTimer.start();
        System.out.println("Send first msg[SYN=1].");

        /* When cntBit is false and timer is not out, resent the SYN message */
        while (this.getcntBit() == 0) {
            if (rxpTimer.checkTimeout()) {
                header.setSyn(true);
                header.setSeqNum(0);
                this.send(null);
                System.out.println("Re-Send first msg[SYN=1].");
                rxpTimer.start();
            }
        }

        /* When cntBit is true, and timer is out, resent the SYN message */
        while (this.getcntBit() == 1) {
            if (rxpTimer.checkTimeout()) {
                header.setSyn(false);
                header.setSeqNum(1);
                this.send(null);
                System.out.println("Re-Send first msg[SYN=0].");
                rxpTimer.start();
            }
        }

        header.setCnt(false);
        System.out
                .println("Connection established...");
    }

    /**
     * When user type "disconnect" command,it will close connection. cntBit :
     * connection flag. cntBit = 2 : connection established. cntBit = 3 :
     * closing wait
     * 
     * @throws IOException
     */
    public void close() throws IOException {
        header.setCnt(true);

        /* Sending initial msg FIN = 1 */
        header.setFin(true);
        header.setSeqNum(0);
        this.send(null);
        System.out.println("Send first msg[FIN=1].");
        rxpTimer.start();

        while (this.getcntBit() == 2) {
            if (rxpTimer.checkTimeout()) {
                header.setFin(true);
                header.setSeqNum(0);
                this.send(null);
                System.out.println("Re-Send first msg[FIN=1].");
                rxpTimer.start();
            }
        }

        while (this.getcntBit() == 3) {
            if (rxpTimer.checkTimeout()) {
                header.setFin(false);
                header.setSeqNum(1);
                this.send(null);
                System.out.println("Re-Send first msg[FIN=0].");
                rxpTimer.start();
            }
        }

        header.setCnt(false);
        System.out
                .println("Connection Closed...");
        this.init();
    }

    /**
     * Listening the incoming request including connect request, get, post, and
     * data action by checking the received packet contents
     * 
     * @throws IOException
     */
    public void listen() throws IOException {
        while (true) {
            socket.receive(recvPacket);
            byte[] realData = null;
            realData = new byte[recvPacket.getLength()];
            System.arraycopy(recvPacket.getData(), 0, realData, 0,
                    recvPacket.getLength());

            if (this.validateChecksum(realData)) {
                RxPHeader tempHeader = this.getHeader(realData);
                if (tempHeader.isCnt()) {
                    recvCntPkt(realData);
                } else if (tempHeader.isGet()) {
                    recvGetPkt(realData);
                } else if (tempHeader.isPost()) {
                    recvPostPkt(realData);
                } else if (tempHeader.isDat()) {
                    recvDataPkt(realData);
                }
            } else {
                System.out.println("Received corrupted data, dropped.");
            }
        }
    }
    
    /**
     * client uses getFile method to get a file from server side protocol sends
     * the requested file to client side
     * 
     * @param filename
     * @throws IOException
     */
    public void getFile(String filename) throws IOException {
        if (cntBit == 2) {
            // ---------------- Request Get file -------------------
            byte[] fileInBytes = filename.getBytes();
            header.setGet(true);
            header.setSeqNum(0);
            this.send(fileInBytes);
            header.setGet(false);
            System.out.println("Sending Get initialize msg.");
            rxpTimer.start();

            // checking the time out situation
            while (this.getGetBit() == 0) {
                if (rxpTimer.checkTimeout()) {
                    header.setGet(true);
                    header.setSeqNum(0);
                    this.send(fileInBytes);
                    header.setGet(false);
                    System.out.println("Re-send Get initialize msg.");
                    rxpTimer.start();
                }
            }

            System.out.println("Start receiving file.");
        } else {
            System.out.println("no connection.");
        }
    }
    
    /**
     * Sending file to the server.
     * 
     * @param filename
     * @throws IOException
     */
    public void postFile(String filename) throws IOException {
        if (cntBit == 2) {
            //Initialize Post file
            FileInputStream fileIn = new FileInputStream(
                    System.getProperty("user.dir") + "/" + filename);
            byte[] fileInBytes = filename.getBytes();

            header.setPost(true);
            header.setSeqNum(0);
            this.send(fileInBytes);
            header.setPost(false);
            System.out.println("Sending Post initialize msg.");
            rxpTimer.start();

            // when postbit is 0, and timer is out, keep sending the post
            // request
            while (this.getPostBit() == 0) {
                if (rxpTimer.checkTimeout()) {
                    header.setPost(true);
                    header.setSeqNum(0);
                    this.send(fileInBytes);
                    header.setPost(false);
                    System.out.println("Re-send Post initialize msg.");
                    rxpTimer.start();
                }
            }

            //Start sending file
            transTimer.start();
            int filesize = 0;

            byte[] buffer = new byte[RxP.BUFFERMAX - RxPHeader.headerLen];
            int payloadLen = fileIn.read(buffer);
            byte[] payload;
            rxpTimer.start();

            // when queuebuffer is not empty, keep sending data
            while (payloadLen != -1 || !queueBuffer.isEmpty()) {

                // check if timer is out, start from the start window
                if (rxpTimer.checkTimeout()) {
                    rxpWindow.setNextToSend(rxpWindow.getStartWindow());
                    rxpTimer.start();
                    ArrayList<byte[]> queue = queueBuffer.returnArrayList();
                    for (int i = 0; i < queue.size(); i++) {
                        if (payloadLen == -1) {
                            if (i == (queue.size() - 1)) {
                                header.setEnd(true);
                            }
                        }
                        int seq = rxpWindow.getNextToSend();
                        header.setSeqNum(seq);
                        header.setDat(true);
                        this.send(queue.get(i));
                        header.setDat(false);
                        header.setEnd(false);
                        rxpWindow.setNextToSend(seq + 1);
                    }
                }

                if (rxpWindow.getNextToSend() <= rxpWindow.getEndWindow()
                        && payloadLen != -1) {
                    filesize += payloadLen;

                    payload = new byte[payloadLen];
                    System.arraycopy(buffer, 0, payload, 0, payloadLen);
                    payloadLen = fileIn.read(buffer);
                    if (payloadLen == -1) {
                        header.setEnd(true);
                    }
                    int seq = rxpWindow.getNextToSend();
                    header.setSeqNum(seq);
                    header.setDat(true);
                    this.send(payload);
                    header.setDat(false);
                    header.setEnd(false);
                    rxpWindow.setNextToSend(seq + 1);
                    queueBuffer.enqueue(payload);
                }
            }

            double transTime = transTimer.getTime();
            System.out.println("Transmission time: " + transTime + " secs");
            System.out.printf("ThroughPut: %.5f  Kbps\n",
                    (double) filesize / (transTime * 1024));

            fileIn.close();
            this.setPostBit(0);
            this.setGetBit(0);
            header.setEnd(false);
            System.out.println("File " + filename + " has been succesfully transimtted.");
        } else {
            System.out.println("no connection.");
        }
    }
    
    /**
     * Set the window size.
     * 
     * @param windowSize
     */
    public void setWindowSize(int windowSize) {
        if (cntBit == 2) {
            this.rxpWindow.setWindowSize(windowSize);
            System.out.println("The window size has been changed to "
                    + windowSize);
        } else {
            System.out.println("Please initialize connection first.");
        }
    }

    /**
     * receive connection establishment packet
     * 
     * @param packet
     * @throws IOException
     */
    public void recvCntPkt(byte[] packet) throws IOException {
        RxPHeader tempHeader= this.getHeader(packet);
        int seq = tempHeader.getSeqNum();
        header.setAckNum(seq);
        /* three time handshake, server receive first SYN or client receive SYN */
        if (this.getcntBit() == 0) {
            // Sever side: received SYN message, send back ACK to Client
            if (tempHeader.isSyn()) {
                System.out
                        .println("Received connection initializing msg [SYN=1]");
                header.setCnt(true);
                this.sendAck();
                this.setcntBit(1);
            }
            // Client Side: received first ACK from server, sending send SYN to
            // server.
            else if (header.isSyn() && tempHeader.isAck()) {
                header.setSyn(false);
                header.setSeqNum(1);
                this.send(null);
                System.out
                        .println("Received first SYN ack, sending second msg[SYN=0].");
                this.setcntBit(1);
            }
            // server received SYN from client, and sent back ACK to client
            else if (!tempHeader.isFin() && !tempHeader.isAck()) {
                header.setCnt(true);
                this.sendAck();
                header.setCnt(false);
            }
        }
        /* received first income SYN message */
        else if (this.getcntBit() == 1) {
            // if message neither SYN or ACK, means it is actual data
            // established the connection
            if (!tempHeader.isAck() && !tempHeader.isSyn()) {
                this.setcntBit(2);
                this.sendAck();
                header.setCnt(false);
                System.out
                        .println("Connection established...");

            }
            // if message is SYN and Sequence number is 0, then it is second
            // handshake
            // sent back ACK to client
            if (tempHeader.getSeqNum() == 0 && tempHeader.isSyn()) {
                header.setCnt(true);
                this.sendAck();
                header.setCnt(false);
            }
            // if message is an ACK, means its client's second ACK
            // connection established
            if (tempHeader.isAck()) {
                this.setcntBit(2);
            }
        }
        /* when connection is established */
        else if (this.getcntBit() == 2) {
            // check is it the last receive packet, if so close connection
            if (tempHeader.isFin()) {
                System.out.println("Received connection closing msg [FIN=1]");
                header.setCnt(true);
                this.sendAck();
                this.setcntBit(3);
            }
            // check Client Side receive ACK and fin packet
            else if (header.isFin() && tempHeader.isAck()) {
                header.setFin(false);
                header.setSeqNum(1);
                this.send(null);
                System.out
                        .println("Received first FIN ack, sending second msg[FIN=0].");
                this.setcntBit(3);
            }
            // if packet is actual data, just sent back ACK
            else if (!tempHeader.isAck() && !tempHeader.isSyn()) {
                header.setCnt(true);
                this.sendAck();
                header.setCnt(false);
            }

        }
        /* When closing connection */
        else if (this.getcntBit() == 3) {
            // server receive actual data
            if (!tempHeader.isAck() && !tempHeader.isFin()) {
                this.setcntBit(0);
                this.sendAck();
                header.setCnt(false);
                this.init();
                System.out.println("Connection Close...");
            }
            // server receive client's last packet, sent a ACK to client
            else if (tempHeader.getSeqNum() == 0 && tempHeader.isFin()) {
                header.setCnt(true);
                this.sendAck();
                header.setCnt(false);
            }
            // Client side received server's close ack
            else if (tempHeader.isAck()) {
                this.setcntBit(0);
            }
        }

        flushRecvPacket();
    }
    

    /**
     * Handle received data transmission packet.
     * 
     * @param packet
     * @throws IOException
     */
    synchronized public void recvDataPkt(byte[] packet) throws IOException {
        RxPHeader tempHeader = this.getHeader(packet);
        // when packet is an ACK packet
        if (tempHeader.isAck()) {
            System.out.println("Received Data ACK Num:"
                    + tempHeader.getAckNum());
            if (tempHeader.getAckNum() == rxpWindow.getStartWindow()) {
                rxpTimer.start();
                rxpWindow.setStartWindow(rxpWindow.getStartWindow() + 1);
                rxpWindow.setEndWindow(rxpWindow.getEndWindow() + 1);
                queueBuffer.dequeue();
            }
        } else {
            //
            if (outBuffer == null){
                throw new IOException("outBuffer havent been initialized");
            }else {
                System.out.println("Received Data Packet Seq Num: "
                        + tempHeader.getSeqNum());
                if (recvFileIndex == tempHeader.getSeqNum()) {
                    byte[] payload = this.getContentByte(packet);
                    outBuffer.write(payload, 0, payload.length);
                    outBuffer.flush();
                    recvFileIndex++;
                    if (tempHeader.isEnd()) {
                        fileOut.close();
                        System.out.println("File received...");
                    }
                }

                int seq = tempHeader.getSeqNum();
                if (recvFileIndex > seq) {
                    header.setAckNum(seq);
                } else if (recvFileIndex < seq) {
                    header.setAckNum(recvFileIndex - 1);
                }
                header.setDat(true);
                this.sendAck();
                header.setDat(false);
            }
        }
        this.flushRecvPacket();
    }

    /**
     * Handle get file packet
     * 
     * @param packet
     * @throws IOException
     */
    public void recvGetPkt(byte[] packet) throws IOException {
        RxPHeader tempHeader = this.getHeader(packet);
        int seq = tempHeader.getSeqNum();
        header.setAckNum(seq);
        if (tempHeader.isAck()) {
            this.setGetBit(1);
        } else {
            if (this.getGetBit() == 0) {
                byte[] payload = this.getContentByte(packet);
                String fileName = new String(payload);
                this.setGetBit(1);
                SendThread sendThread = new SendThread(this, fileName);
                threadList.add(sendThread);
                sendThread.start();
            }
            header.setGet(true);
            this.sendAck();
            header.setGet(false);
        }
        flushRecvPacket();
    }

    /**
     * Handle post file packet
     * 
     * @param packet
     * @throws IOException
     */
    public void recvPostPkt(byte[] packet) throws IOException {
        RxPHeader tempHeader = this.getHeader(packet);
        int seq = tempHeader.getSeqNum();
        header.setAckNum(seq);
        if (this.getPostBit() == 0) {
            if (tempHeader.isAck()) {
                this.setPostBit(1);
            } else {
                // Getting data from the input file
                byte[] payload = this.getContentByte(packet);
                String fileName = new String(payload);
                fileOut = new FileOutputStream(System.getProperty("user.dir")
                        + "/" + fileName, true);
                outBuffer = new BufferedOutputStream(fileOut);
                header.setPost(true);
                this.sendAck();
                header.setPost(false);
            }
        }
        flushRecvPacket();
    }
    
    /**
     * Protocol send incoming data into Datagrams through UDP socket the data
     * need to be add check sum before sending
     * 
     * @param data
     * @throws IOException
     */
    synchronized public void send(byte[] data) throws IOException {
        header.setAck(false);
        byte[] dataWithHeader = pack(header.getHeader(), data);
        dataWithHeader = this.addChecksum(dataWithHeader);
        System.out
                .println("Sending packet#:" + header.getSeqNum());
        sendPacket = new DatagramPacket(dataWithHeader, dataWithHeader.length,
                serverAddress, netEmuPort);
        socket.send(sendPacket);
    }   

 

    /**
     * Getting header's ack number and add check sum to this ack number then
     * send new ACK through UDP socket
     * 
     * @throws IOException
     */
    synchronized public void sendAck() throws IOException {
        System.out.println("SendingAck#: " + header.getAckNum());
        header.setAck(true);
        byte[] dataToSend = this.addChecksum(header.getHeader());
        sendPacket = new DatagramPacket(dataToSend, RxPHeader.headerLen,
                serverAddress, netEmuPort);
        socket.send(sendPacket);
    }
    
    /**
     * Convert the ASCII byte[] data into String
     */
    public String byteArrayToString(byte[] data) {
        StringBuilder buffer = new StringBuilder(data.length);
        for (int i = 0; i < data.length; ++i) {
            if (data[i] < 0)
                throw new IllegalArgumentException();
            buffer.append((char) data[i]);
        }
        return buffer.toString();
    }

    /**
     * Getting the header information from received data
     */
    public RxPHeader getHeader(byte[] receiveData) {
        RxPHeader header = new RxPHeader();
        int headerLen = receiveData[12];
        byte[] headerArray = new byte[headerLen];
        System.arraycopy(receiveData, 0, headerArray, 0, headerLen);
        header.headerFromArray(headerArray);

        return header;
    }

    /**
     * Getting the actual content from received data
     */
    public byte[] getContentByte(byte[] receiveData) {
        int headerLen = receiveData[12];
        byte[] content = new byte[receiveData.length - headerLen];
        System.arraycopy(receiveData, headerLen, content, 0, receiveData.length
                - headerLen);
        return content;
    }
    
    /**
     * Flush the received data Package.
     */
    synchronized public void flushRecvPacket() {
        recvPacket = new DatagramPacket(new byte[BUFFERMAX], BUFFERMAX);
    }
    
    /**
     * Packing header array and data array into a new array, so that we can send
     * this new data to the UDP socket
     * 
     * @param header header byte[]
     * @param data data byte[]
     * @return result the single byte[] array
     */
    static byte[] pack(byte[] header, byte[] data) {

        if (data != null) {
            int headerLen = header.length;
            int totalLen = headerLen + data.length;
            byte[] result = new byte[totalLen];

            for (int i = 0; i < headerLen; i++) {
                result[i] = header[i];
            }
            int j = 0;
            for (int i = headerLen; i < totalLen; i++) {
                result[i] = data[j];
                j++;
            }
            return result;
        } else {
            return header;
        }

    }

    /**
     * Before sending the packet, we have to add a check sum field into each
     * packet to make sure the correction of data
     * 
     * @param packet
     * @return
     */
    public byte[] addChecksum(byte[] packet) {
        int len = packet.length;
        short[] words = new short[len / 2];
        for (int i = 0; i < len - 1; i = i + 2) {
            if (i  < len - 1) {
                short a = (short) (((((int) (packet[i])) & 0x0000FFFF) << 8) | (((int) (packet[i + 1])) & 0x000000FF));
                words[i / 2] = a;
            } else {
                short a = (short) (((((int) (packet[i])) & 0x0000FFFF) << 8) | (int) 0);
                words[i / 2] = a;
            }
        }
        short checksum = 0;
        for (int i = 0; i < words.length; i++) {
            int temp = ((int) checksum & 0x0000FFFF)
                    + ((int) words[i] & 0x0000FFFF);
            if ((temp & 0x10000) == 0x10000) {
                temp++;
            }
            checksum = (short) temp;
        }
        checksum = (short) (((int) checksum & 0x0000FFFF) ^ 0xFFFF);
        packet[14] = (byte) (checksum >> 8);
        packet[15] = (byte) (checksum & 0xFF);
        return packet;
    }

    /**
     * Using this check sum function to check every received packet's corruption
     * 
     * @param packet
     * @return
     */
    public boolean validateChecksum(byte[] packet) {
        boolean correct = false;
        int len = packet.length;
        short[] words = new short[len / 2];

        for (int i = 0; i < len - 1; i = i + 2) {
            if (i < len - 1) {
                short a = (short) (((((int) (packet[i])) & 0x0000FFFF) << 8) | (((int) (packet[i + 1])) & 0x000000FF));
                words[i / 2] = a;
            } else {
                short a = (short) (((((int) (packet[i])) & 0x0000FFFF) << 8) | (int) 0);
                words[i / 2] = a;
            }
        }
        short checksum = 0;
        for (int i = 0; i < words.length; i++) {
            int temp = 0;
            temp = ((int) checksum & 0x0000FFFF) + ((int) words[i] & 0x0000FFFF);
            if ((temp & 0x10000) == 0x10000) {
                temp++;
            }
            checksum = (short) temp;
        }
        if ((checksum & 0xFFFF) == 0xFFFF) {
            correct = true;
        }
        return correct;
    }

  
  /*--------------------------------------getter & setter------------------------------*/  
    public DatagramSocket getSocket() {
        return socket;
    }

    public void setSocket(DatagramSocket socket) {
        this.socket = socket;
    }

    public InetAddress getServerAddress() {
        return serverAddress;
    }

    public void setServerAddress(InetAddress serverAddress) {
        this.serverAddress = serverAddress;
    }

    public int getemuPort() {
        return netEmuPort;
    }

    public void setemuPort(int emuPort) {
        this.netEmuPort = emuPort;
    }

    public int getDestPort() {
        return destPort;
    }

    public void setDestPort(int destPort) {
        this.destPort = destPort;
    }

    public int gethostPort() {
        return hostPort;
    }

    public void sethostPort(int hostPort) {
        this.hostPort = hostPort;
    }

    synchronized public RxPHeader getHeader() {
        return header;
    }

    synchronized public void setHeader(RxPHeader header) {
        this.header = header;
    }

    synchronized public int getcntBit() {
        return cntBit;
    }

    synchronized public void setcntBit(int cntBit) {
        this.cntBit = cntBit;
    }

    synchronized public int getGetBit() {
        return getBit;
    }

    synchronized public void setGetBit(int getBit) {
        this.getBit = getBit;
    }

    synchronized public int getPostBit() {
        return postBit;
    }

    synchronized public void setPostBit(int postBit) {
        this.postBit = postBit;
    }

    public ArrayList<SendThread> getThreadList() {
        return threadList;
    }

    public void setThreadList(ArrayList<SendThread> threadList) {
        this.threadList = threadList;
    }
    

    public class QueueBuffer<T> {

        
        // head and tail node
        private Node first, last;
        // size of the queue
        private int total;

        /**
         * node structure as linked list
         */
        private class Node {
            private T e;
            private Node next;
        }

        /**
         * default constructor 
         */
        public QueueBuffer() {
            first = null;
            last = null;
        }

        /**
         * enqueue method
         * 
         * Add element into the end of queue.
         * 
         * @param e - element to be added
         * @return queue
         */
        synchronized public QueueBuffer<T> enqueue(T e) {
            Node current = last;
            last = new Node();
            last.e = e;
            if (total++ == 0)
                first = last;
            else
                current.next = last;

            return this;
        }

        /**
         * dequeue method
         * remove the first element in the queue 
         * and return it
         * 
         * @return first element in the queue
         */
        synchronized public T dequeue() {
            // trying to remove empty queue
            if (total == 0)
                throw new java.util.NoSuchElementException();
            
            T e = first.e;
            first = first.next;
            if (--total == 0) {
                first = null;
                last = null;
            }
            return e;
        }
        
        /**
         * convert the queue into array list
         * @return array list containing all the element in the queue
         */
        public ArrayList<T> returnArrayList() {
            ArrayList<T> list = new ArrayList<T>();
            Node n = this.first;
            for (int i = 0; i < this.total; i++) {
                list.add(n.e);
                n = n.next;
            }
            return list;
        }

        /**
         * to string method
         */
        public String toString() {
            StringBuilder sb = new StringBuilder();
            Node tmp = first;
            while (tmp != null) {
                sb.append(tmp.e).append(", ");
                tmp = tmp.next;
            }
            return sb.toString();
        }

        
        public boolean isEmpty() {
            return (first == null);
        }

        public int size() {
            return total;
        }

    }
}
