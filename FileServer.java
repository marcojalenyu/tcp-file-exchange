/**
 * CSNETWK S17
 * Teves, Hannah Juliet M.
 * Yu, Marco Jalen D.
 */

import java.net.*;
import java.io.*;

public class FileServer
{
	public static void main(String[] args)
	{
		int nPort = Integer.parseInt(args[0]);
		System.out.println("Server: Listening on port " + args[0] + "...\n");
		ServerSocket serverSocket;
		Socket serverEndpoint;

		try 
		{
			serverSocket = new ServerSocket(nPort);
			serverEndpoint = serverSocket.accept();
			
			System.out.println("Server: New client connected: " + serverEndpoint.getRemoteSocketAddress() + "\n");

			// Create input stream (to get Download.txt)
			File file = new File("Download.txt");
			DataInputStream disReader = new DataInputStream(new FileInputStream(file));

			// Convert file to bytes (to copy the contents)
			byte[] buffer = new byte[(int) file.length()];
			disReader.readFully(buffer);
			
			// Create output stream to send Download.txt to Client
			DataOutputStream dosWriter = new DataOutputStream(serverEndpoint.getOutputStream());
			dosWriter.writeInt(buffer.length);
			dosWriter.write(buffer);

			// Close all streams and confirmation message
			System.out.println("Sending file \"Download.txt\" (" + (int) buffer.length + " bytes)\n");
			disReader.close();
			dosWriter.close();
			serverEndpoint.close();
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		finally
		{
			System.out.println("Server: Connection is terminated.");
		}
	}
}