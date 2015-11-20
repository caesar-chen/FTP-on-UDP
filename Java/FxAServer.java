import java.io.IOException;
import java.net.InetAddress;
import java.util.Scanner;

/*
 * FxAServer
 * 
 * deals with the server side command line arguments and supports the following functions:
 * start server
 * Window (w) - change window size, default window size = 2
 * terminate - terminate the server
 */

public class FxAServer {

	public static void main(String[] args) throws IOException {

		System.out.println("server starts");
		Scanner scanner = new Scanner(System.in);

		// check command line arguments
		if (args.length != 3) {
			throw new IOException(
					"Invalid Argument, please enter 3 arguments for server socket, NetEmu IP, NetEmu port");
		}

		String log = "output-server.txt";

		// pass server port number, emulator IP, emulator Port Number from
		// command line argument

		int hostPort = Integer.parseInt(args[0]);
		// Server IP address
		InetAddress serverIP = InetAddress.getByName(args[1]);
		// netEmu port number
		int netEmuPort = Integer.parseInt(args[2]);
		// Dest. port number
		int desPort = hostPort - 1;
		RxP rxpProtocol = new RxP(serverIP, netEmuPort, hostPort, desPort, log);

		// Start the server and ready for sending and receiving data
		Thread serverProtocol = new RecvThread(rxpProtocol);
		serverProtocol.start();

		while (true) {
			System.out.println("type Window W - to change the window size \n"
					+ "terminate - to terminate the server");

			String input = scanner.nextLine();

			if (input.contains("window")) { // change window size
				String[] s = input.split("\\s");
				int wsize = Integer.parseInt(s[1]);
				rxpProtocol.setWindowSize(wsize);

			} else if (input.equals("terminate")) {
				rxpProtocol.close();
				serverProtocol.stop();
				for (SendThread t : rxpProtocol.getThreadList()) {
					t.stop();
				}
				rxpProtocol.getSocket().close();
				System.out.println("Server has been terminated.");
				break;
			}
		}
	}
}
