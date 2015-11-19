import java.io.IOException;


public class SendThread extends Thread {
	RxP rxp;
	String filename;
	
	public SendThread(RxP rxp, String filename){
		this.rxp = rxp;
		this.filename = filename;
	}
	// run a file sending thread
	@Override
	public void run() {
		try {
			rxp.postFile(filename);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
