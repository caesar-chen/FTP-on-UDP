/**
 * RxP Timer class, deal with time out related issues
 * 
 *
 */
public class RxPTimer {

	private long time;
	public static final double TIMEOUT = 1;

	// default constructor
	public RxPTimer() {
		super();
		this.time = 0;
	}

	/**
	 * start timer, get the current time
	 */
	public void start() {
		this.time = System.currentTimeMillis();
	}

	
	/**
	 * calculate the time difference between current time 
	 * and the time when timer starts, in seconds 
	 * 
	 * @return time difference
	 */
	public double getTime() {
		return (double) ((System.currentTimeMillis() - time) / 1000);
	}

	/**
	 * Checks if timeout occurs
	 * 
	 * @return true - if timeout
	 * 		   false - no timeout
	 */
	public boolean checkTimeout() {
		// calculate the time difference between two times,
		// if less than 1 sec, no timeout and return false
		if (System.currentTimeMillis() - this.time < 1000 * TIMEOUT) {
			return false;
		} else {
			// longer than 1sec, timeout and return true
			return true;
		}
	}

}
