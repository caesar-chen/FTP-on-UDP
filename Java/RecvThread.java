import java.io.IOException;


public class RecvThread extends Thread{
	RxP rxp;
	
	public RecvThread(RxP rxp){
		this.rxp = rxp;
	}

	// run a thread to listen all the incoming data.
	@Override
	public void run() {
		try {
			rxp.listen();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
