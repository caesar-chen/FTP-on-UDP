/**
 * class represents RxP protocol header
 * 
 */
public class RxPHeader {
	
	short sourcePort; // The port number of the packet source
	short destPort; // The port number of the packet destination
	int seqNum; // Current sequence number for the packet
	int ackNum; // The acknowledgement number
	final static int headerLen = 16; // header length
	boolean ack; // bit to indicate package is ack package
	boolean end; // bit to indicate if the package is the last package
	boolean dat; // bit to indicate if the package is data package
	boolean cnt; // bit to indicate if the package contains connection data
	boolean syn; // bit to initiate a connection
	boolean fin; // bit to close a connection
	boolean get; // bit for get file request
	boolean post; // bit for post file request
	short checksum; // Checksum field
	byte[] header; // Byte array of header for sending

	/**
	 * default constructor which should not be called
	 */
	public RxPHeader() {
		super();
		this.sourcePort = -1;
		this.destPort = -1;
		this.seqNum = -1;
		this.ackNum = -1;
		this.ack = false;
		this.end = false;
		this.dat = false;
		this.cnt = false;
		this.syn = false;
		this.fin = false;
		this.get = false;
		this.post = false;
		this.checksum = -1;
		this.header = new byte[headerLen];
	}

	/**
	 * constructor for RXPHeader
	 * 
	 * @param sourcePort
	 * @param destPort
	 * @param seqNum
	 * @param ackNum
	 */
	public RxPHeader(short sourcePort, short destPort, int seqNum, int ackNum) {
		super();
		this.sourcePort = sourcePort;
		this.destPort = destPort;
		this.seqNum = seqNum;
		this.ackNum = ackNum;
		this.ack = false;
		this.end = false;
		this.dat = false;
		this.cnt = false;
		this.syn = false;
		this.fin = false;
		this.get = false;
		this.post = false;
		this.checksum = 0;
		this.header = new byte[headerLen];
	}

	/**
	 * convert all instance variables of RxP header into header (byte array)
	 * 
	 * @return header - the byte array containing all instance variables of RxP
	 *         header
	 */
	public byte[] setHeader() {
		this.header[0] = (byte) (this.sourcePort >> 8);
		this.header[1] = (byte) (this.sourcePort & 0xFF);
		this.header[2] = (byte) (this.destPort >> 8);
		this.header[3] = (byte) (this.destPort & 0xFF);
		this.header[4] = (byte) (this.seqNum >> 24);
		this.header[5] = (byte) (this.seqNum >> 16);
		this.header[6] = (byte) (this.seqNum >> 8);
		this.header[7] = (byte) (this.seqNum & 0xFF);
		this.header[8] = (byte) (this.ackNum >> 24);
		this.header[9] = (byte) (this.ackNum >> 16);
		this.header[10] = (byte) (this.ackNum >> 8);
		this.header[11] = (byte) (this.ackNum & 0xFF);
		this.header[12] = (byte) (RxPHeader.headerLen & 0xFF);
		this.header[13] = 0;
		if (fin) {
			this.header[13] = (byte) (this.header[13] | 0x1);
		}
		if (syn) {
			this.header[13] = (byte) (this.header[13] | 0x2);
		}
		if (cnt) {
			this.header[13] = (byte) (this.header[13] | 0x4);
		}
		if (dat) {
			this.header[13] = (byte) (this.header[13] | 0x8);
		}
		if (ack) {
			this.header[13] = (byte) (this.header[13] | 0x10);
		}
		if (end) {
			this.header[13] = (byte) (this.header[13] | 0x20);
		}
		if (get) {
			this.header[13] = (byte) (this.header[13] | 0x40);
		}
		if (post) {
			this.header[13] = (byte) (this.header[13] | 0x80);
		}
		this.header[14] = (byte) (this.checksum >> 8);
		this.header[15] = (byte) (this.checksum & 0xFF);
		return this.header;
	}

	/**
	 * given a byte array header, convert it into a RxPHeader object.
	 * 
	 * @param header
	 */
	public void headerFromArray(byte[] header) {
		this.sourcePort = (short) (header[0] << 8 | ((short) 0 | 0xFF)
				& header[1]);
		this.destPort = (short) (header[2] << 8 | ((short) 0 | 0xFF)
				& header[3]);
		this.seqNum = (int) (header[4] << 24 | header[5] << 16 | header[6] << 8 | ((short) 0 | 0xFF)
				& header[7]);
		this.ackNum = (int) (header[8] << 24 | header[9] << 16
				| header[10] << 8 | ((short) 0 | 0xFF) & header[11]);
		if ((byte) (header[13] & 0x1) == (byte) 0x1) {
			this.fin = true;
		}
		if ((byte) (header[13] & 0x2) == (byte) 0x2) {
			this.syn = true;
		}
		if ((byte) (header[13] & 0x4) == (byte) 0x4) {
			this.cnt = true;
		}
		if ((byte) (header[13] & 0x8) == (byte) 0x8) {
			this.dat = true;
		}
		if ((byte) (header[13] & 0x10) == (byte) 0x10) {
			this.ack = true;
		}
		if ((byte) (header[13] & 0x20) == (byte) 0x20) {
			this.end = true;
		}
		if ((byte) (header[13] & 0x40) == (byte) 0x40) {
			this.get = true;
		}
		if ((byte) (header[13] & 0x80) == (byte) 0x80) {
			this.post = true;
		}
		this.checksum = (short) (header[14] << 8 | ((short) 0 | 0xFF)
				& header[15]);
	}

	// getters and setters for instance variables
	public byte[] getHeader() {
		this.header = setHeader();
		return header;
	}

	public void setHeader(byte[] header) {
		this.header = header;
	}

	public short getSourcePort() {
		return sourcePort;
	}

	public void setSourcePort(short sourcePort) {
		this.sourcePort = sourcePort;
	}

	public short getDestPort() {
		return destPort;
	}

	public void setDestPort(short destPort) {
		this.destPort = destPort;
	}

	public int getSeqNum() {
		return seqNum;
	}

	public void setSeqNum(int seqNum) {
		this.seqNum = seqNum;
	}

	public int getAckNum() {
		return ackNum;
	}

	public void setAckNum(int ackNum) {
		this.ackNum = ackNum;
	}

	public boolean isEnd() {
		return end;
	}

	public void setEnd(boolean end) {
		this.end = end;
	}

	public boolean isAck() {
		return ack;
	}

	public void setAck(boolean ack) {
		this.ack = ack;
	}

	public boolean isDat() {
		return dat;
	}

	public void setDat(boolean dat) {
		this.dat = dat;
	}

	public boolean isCnt() {
		return cnt;
	}

	public void setCnt(boolean cnt) {
		this.cnt = cnt;
	}

	public boolean isSyn() {
		return syn;
	}

	public void setSyn(boolean syn) {
		this.syn = syn;
	}

	public boolean isFin() {
		return fin;
	}

	public void setFin(boolean fin) {
		this.fin = fin;
	}

	public boolean isGet() {
		return get;
	}

	public void setGet(boolean get) {
		this.get = get;
	}

	public boolean isPost() {
		return post;
	}

	public void setPost(boolean post) {
		this.post = post;
	}

	public short getChecksum() {
		return checksum;
	}

	public void setChecksum(short checksum) {
		this.checksum = checksum;
	}

	static int getHeaderLen() {
		return headerLen;
	}

	public String toString() {
		return header.toString();
	}

}
