/* 
 * Section: S17
 * Names: 	Teves, Hannah Juliet	
 * 			Yu, Marco Jalen
 * 
 */

import java.net.*;
import java.io.*;

public class ChatClient
{
	public static void main(String[] args)
	{
		String sServerAddress = args[0];
		int nPort = Integer.parseInt(args[1]);
		String sUsername = args[2];
		String sMessage = args[3];
		
		try
		{
			Socket clientEndpoint = new Socket(sServerAddress, nPort);
			
			System.out.println(sUsername + ": Connected to server at " + clientEndpoint.getRemoteSocketAddress() + "\n");
			System.out.println(sUsername + ": Connected to server at " + clientEndpoint.getRemoteSocketAddress() + "\n");
			
			DataOutputStream dosWriter = new DataOutputStream(clientEndpoint.getOutputStream());
			dosWriter.writeUTF(sUsername);
			dosWriter.writeUTF(sMessage);
			
			DataInputStream disReader = new DataInputStream(clientEndpoint.getInputStream());
			System.out.println(disReader.readUTF());
		
			clientEndpoint.close();
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		finally
		{
			System.out.println(sUsername + ": Connection is terminated.");
		}
	}
}