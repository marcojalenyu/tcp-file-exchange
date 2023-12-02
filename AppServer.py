from socket import *
import threading

# Server Port Number
serverPort = 12345

# Stores existing handle/alias
handles = {}

# Preparing the Server Socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

# To deal with a Client
def manageClient(connectionSocket, addr):
    # Send and receive message for new
    print("Device from port number " + str(addr[1]) + " connected to the server.\n")

    try:
        connectionSocket.send("Connection to the File Exchange Server is successful!".encode())

        # How the Server responds to the commands from Client
        while True:
            command = connectionSocket.recv(1024).decode()      

            # If the Client leaves      
            if command == "/leave":
                connectionSocket.send("Connection closed. Thank you!".encode())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Device from port number " + str(addr[1]) + " disconnected from the server.\n")
        connectionSocket.close()

while True:
    # Establishing the connection
    print('The server is ready to receive.')
    connectionSocket, addr = serverSocket.accept()
    threading.Thread(target=manageClient, args=(connectionSocket, addr)).start()

