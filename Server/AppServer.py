from socket import *
import os
import threading
import struct
from datetime import datetime

# Server Port Number
serverPort = 12345

# Stores existing handle/alias
clients = {}

# Stores the files in the server's working directory
folder_name = "Files"
folder_path = os.path.join(os.getcwd(), folder_name)
os.makedirs(folder_path, exist_ok=True)

# Preparing the Server Socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

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
                    connectionSocket.send(("Welcome "+handle+"!\n").encode())
                    print("Device from port number " + str(addr[1]) + " registered as "+handle+".\n")
                else:
                    connectionSocket.send("Error: Registration failed. Handle or alias already exists.".encode())
                    print("Device from port number " + str(addr[1]) + " failed to register as the handle or alias already exists.\n")
                
            # If the Client sends a file to the Server
            elif command == "/store":
                try:
                    file_path = connectionSocket.recv(1024).decode()
                    filename = os.path.basename(file_path)

                    print("Device from port number " + str(addr[1]) + " requested to upload " + filename + ".\n")

                    # Check if the file exists
                    if os.path.exists(file_path):
                        filesize = struct.unpack("!Q", connectionSocket.recv(8))[0]
                        data = connectionSocket.recv(filesize)

                        # Create a new file
                        server_path = os.path.join(folder_path, filename)
                        with open(server_path, 'wb') as f:
                            f.write(data)

                        timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        connectionSocket.send((handle + "<" + timestamp + ">: Uploaded " + filename).encode())
                        print("Device from port number " + str(addr[1]) + " uploaded " + filename + ".\n")

                        # Add the file to the list of files in the server's working directory
                        file_list.append(filename)
                except Exception as e:
                    print(f"Error: {e}")

           # If the Client requests directory file list from the Server
            elif command == "/dir":
                try:
                    print("Device from port number " + str(addr[1]) + " requested for the list of files in the server.\n")
                    
                    # Send the list of files to the client
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        file_list = os.listdir(folder_path)
                        connectionSocket.send(str(file_list).encode())
                    else:
                        connectionSocket.send("[]".encode())  # Send an empty list as a string

                except Exception as e:
                    print(f"Error: {e}")

           # If the Client requests to fetch a file from the Server
            elif command == "/get":
                # Receive the filename from the client
                filename = connectionSocket.recv(1024).decode()

                # Get the file path in the server
                server_path = os.path.join(folder_path, filename)

                print(server_path)

                try:
                    # Check if the file exists in the server
                    if not os.path.exists(server_path):
                        connectionSocket.send("Error: File not found in the server.".encode())
                    else:
                        # Read and send the file to the client in chunks
                        with open(server_path, 'rb') as file:
                            file_bytes = file.read()
                            file_size = len(file_bytes)

                            connectionSocket.send(struct.pack("!Q", file_size))
                            connectionSocket.sendall(file_bytes)

                        connectionSocket.send(f"File received from Server: {filename}".encode())
                        print("Device from port number " + str(addr[1]) + " downloaded " + filename + ".\n")

                except Exception as e:
                    print(f"Error: {e}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Device from port number " + str(addr[1]) + " disconnected from the server.\n")
        connectionSocket.close()

# Function to handle each client connection
def start_server():
    while True:
        # Establishing the connection
        print('The server is ready to receive.\n')
        connectionSocket, addr = serverSocket.accept()
        thread = threading.Thread(target=manageClient, args=(connectionSocket, addr))
        thread.start()

# Start the server
start_server()

