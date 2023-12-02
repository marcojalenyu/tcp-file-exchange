from socket import *

# Server Port Number
serverPort = 12345

# Stores existing handle/alias
handles = {}

# Preparing the Server Socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

while True:
    # Establishing the connection
    print('The server is ready to receive.')
    connectionSocket, addr = serverSocket.accept()
    print("Device from port number " + str(addr[1]) + " connected to the server.\n")

    try:
        data = connectionSocket.recv(1024)

        if not data:
             connectionSocket.send("Connection closed. Thank you!".encode())

    except Exception as e:
        print(f"Error: {e}")
        connectionSocket.close()
    
    finally:
        print("Device from port number " + str(addr[1]) + " disconnected from the server.\n")
        connectionSocket.close()