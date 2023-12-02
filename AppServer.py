from socket import *
import threading

# Server Port Number
serverPort = 12345

# Stores existing handle/alias
clients = {}

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
                break

            # If the Client registers (must be unique and new)
            elif command == "/register":
                handle = connectionSocket.recv(1024).decode()
                connectionSocket.send(str(handle in clients).encode())

                if handle not in clients:
                    clients[handle] = {'socket': connectionSocket, 'address': addr}
                    connectionSocket.send(("Welcome "+handle+"!").encode())
                    print("Device from port number " + str(addr[1]) + " registered as "+handle+".\n")
                else:
                    connectionSocket.send("Error: Registration failed. Handle or alias already exists.".encode())
                    print("Device from port number " + str(addr[1]) + " failed to register as the handle or alias already exists.\n")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Device from port number " + str(addr[1]) + " disconnected from the server.\n")
        connectionSocket.close()

while True:
    # Establishing the connection
    print('The server is ready to receive.\n')
    connectionSocket, addr = serverSocket.accept()
    thread = threading.Thread(target=manageClient, args=(connectionSocket, addr))
    thread.start()
    thread.join()

