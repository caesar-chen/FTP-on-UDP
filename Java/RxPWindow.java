/**
 * RxPWindow class
 * deal with window related function
 * changing window size
 * set start window, end window
 *
 *
 */
public class RxPWindow {
	int windowSize;
	int startWindow;
	int endWindow;
	int nextToSend;
	

	public RxPWindow() {
		super();
		this.windowSize = 5;
		this.startWindow = 0;
		this.endWindow = 0 + this.windowSize - 1;
		this.nextToSend = 0;
	}
	
	public int getNextToSend() {
		return nextToSend;
	}

	public void setNextToSend(int nextToSend) {
		this.nextToSend = nextToSend;
	}

	public int getWindowSize() {
		return windowSize;
	}


	public void setWindowSize(int windowSize) {
		this.windowSize = windowSize;
	}


	public int getStartWindow() {
		return startWindow;
	}


	public void setStartWindow(int startWindow) {
		this.startWindow = startWindow;
	}


	public int getEndWindow() {
		return endWindow;
	}


	public void setEndWindow(int endWindow) {
		this.endWindow = endWindow;
	}
	
	

}
