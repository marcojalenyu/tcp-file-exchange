/* 
 * Section: S17
 * Names: 	Teves, Hannah Juliet	
 * 			Yu, Marco Jalen
 * 
 */

import java.net.*;
import java.io.*;

public class ChatServer
{
	public static void main(String[] args)
	{
		int nPort = Integer.parseInt(args[0]);
		
		ServerSocket serverSocket;
		Socket serverEndpoint;

		String clientNameA;
		String clientMessageA;

		String clientNameB;
		String clientMessageB;

		try 
		{
			serverSocket = new ServerSocket(nPort);

			// Client A
			System.out.println("Server: Listening on port " + args[0] + "..." + "\n");
			serverEndpoint = serverSocket.accept();
			
			System.out.println("Server: New client connected: " + serverEndpoint.getRemoteSocketAddress() + "\n");
			
			DataInputStream disReaderA = new DataInputStream(serverEndpoint.getInputStream());
			DataOutputStream dosWriterA = new DataOutputStream(serverEndpoint.getOutputStream());

			clientNameA = disReaderA.readUTF();
			clientMessageA = disReaderA.readUTF();

			// Client B
			System.out.println("Server: Listening on port " + args[0] + "..." + "\n");
			serverEndpoint = serverSocket.accept();

			System.out.println("Server: New client connected: " + serverEndpoint.getRemoteSocketAddress() + "\n");
			
			DataInputStream disReaderB = new DataInputStream(serverEndpoint.getInputStream());
			DataOutputStream dosWriterB = new DataOutputStream(serverEndpoint.getOutputStream());

			clientNameB = disReaderB.readUTF();
			clientMessageB = disReaderB.readUTF();

			// Display messages
			dosWriterA.writeUTF("Message from " + clientNameB + ": " + clientMessageB + "\n");
			dosWriterB.writeUTF("Message from " + clientNameA + ": " + clientMessageA + "\n");		

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