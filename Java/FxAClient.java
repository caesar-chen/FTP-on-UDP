import java.io.IOException;
import java.net.InetAddress;
import java.util.Scanner;

/*
 * FxAClient 
 * 
 * deals with the client side command line arguments and supports the following functions:
 * Connect - to establish connection
 * Get File(File Name) - download the file from server
 * Post File (File Name) - upload the file to server
 * Window (w) - change window size, default window size = 2
 * Disconnect - close the connection
 */

public class FxAClient {

	public static void main(String[] args) throws IOException, InterruptedException {

		RxP rxpProtocol = null;
		Scanner scanner = new Scanner(System.in);

		// check command line argument
		if ((args.length < 3) || (args.length > 4)) {
			throw new IOException("Invalid Argument");
		}

		// pass the command line arguments
		int clientPort = Integer.parseInt(args[0]);
		// Server IP address
		InetAddress serverIP = InetAddress.getByName(args[1]);
		// netEmu port number
		int netEmuPort = Integer.parseInt(args[2]);
		// Dest. port number
		int desPort = clientPort + 1;

		Thread clientProtocol = null;
		Thread sendThread = null;
		String log = "output-client.txt";
		
		// execute user's commend
		while (true) {
			Thread.sleep(500);
			System.out.println("type connect - to establish connection \n"
					+ "get 'filename' - to download the file from server \n"
					+ "post 'filename' - to upload the file to server \n"
					+ "Window W - to change the window size \n"
					+ "disconnect - to close the connection");
			
			String input = scanner.nextLine();
			
			if (input.equals("connect")) {  // establish connection
				rxpProtocol = new RxP(serverIP, netEmuPort, clientPort,
						desPort, log);
				clientProtocol = new RecvThread(rxpProtocol);
				clientProtocol.start();
				rxpProtocol.connect();
				
			} else if (input.contains("get")) { // get file from server
				if (rxpProtocol != null) {
					String[] s = input.split("\\s");
					rxpProtocol.getFile(s[1]);
				}
				
			} else if (input.contains("post")) { // post file to server
				if (rxpProtocol != null) {
					String[] s = input.split("\\s");
					sendThread = new SendThread(rxpProtocol, s[1]);
					sendThread.start();
				}
		

			} else if (input.contains("window")) { // change window size
				if (rxpProtocol != null) {
					
					String[] s = input.split("\\s");
					int window = Integer.parseInt(s[1]);
					rxpProtocol.setWindowSize(window);
				}
				
			} else if (input.equals("disconnect")) { // close connection
				if (rxpProtocol != null) {
					rxpProtocol.close();
					clientProtocol.stop();
					if (sendThread != null) {
						sendThread.stop();
					}
					rxpProtocol.getSocket().close();
				}
			}
		}
	}
	
	
}
