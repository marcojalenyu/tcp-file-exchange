/**
 * CSNETWK S17
 * Teves, Hannah Juliet M.
 * Yu, Marco Jalen D.
 */

import java.net.*;
import java.io.*;

public class FileClient
{
	public static void main(String[] args)
	{
		String sServerAddress = args[0];
		int nPort = Integer.parseInt(args[1]);
		
		try
		{
			Socket clientEndpoint = new Socket(sServerAddress, nPort);
			
			// Connecting to the server...
			System.out.println("Client: Connecting to server at " + clientEndpoint.getRemoteSocketAddress() + "\n");
			System.out.println("Client: Connected to server at " + clientEndpoint.getRemoteSocketAddress() + "\n");
			
			// Create input stream (to get the content of Download.txt from the Server)
			DataInputStream disReader = new DataInputStream(clientEndpoint.getInputStream());
			int fileSize = disReader.readInt();
			byte[] buffer = new byte[fileSize];
			disReader.readFully(buffer);

			// Create output stream (to download Download.txt as Received.txt)
			FileOutputStream fosWriter = new FileOutputStream("Received.txt");
			fosWriter.write(buffer);
		
			// Close all streams and confirmation that file has been downloaded successfully
			System.out.println("Client: Downloaded file \"Received.txt\" \n");
			disReader.close();
			fosWriter.close();
			clientEndpoint.close();
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		finally
		{
			System.out.println("Client: Connection is terminated.");
		}
	}
}