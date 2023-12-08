from socket import *
import os
import threading
from datetime import datetime

# Server Port Number
serverPort = 12345

# Stores existing handle/alias
clients = {}

# Stores the files in the server's working directory
file_list = []

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
                    connectionSocket.send(("Welcome "+handle+"!").encode())
                    print("Device from port number " + str(addr[1]) + " registered as "+handle+".\n")
                else:
                    connectionSocket.send("Error: Registration failed. Handle or alias already exists.".encode())
                    print("Device from port number " + str(addr[1]) + " failed to register as the handle or alias already exists.\n")
                
            # If the Client sends a file to the Server
            elif command == "/store":
                try:
                    filename = connectionSocket.recv(1024).decode()

                    # Check if the file exists
                    if os.path.exists(filename):
                        filesize = int(connectionSocket.recv(1024).decode())
                        # Create a new file
                        with open(filename, 'wb') as f:
                            totalRecv = 0
                            while totalRecv < filesize:
                                data = connectionSocket.recv(1024)
                                totalRecv += len(data)
                                f.write(data)
                                print("{0:.2f}".format((totalRecv/float(filesize))*100)+"% Done")

                        timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        connectionSocket.send((handle + "<" + timestamp + ">: Uploaded " + filename).encode())

                        # Add the file to the list of files in the server's working directory
                        file_list.append(filename)

                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " uploaded " + filename + ".\n")
                    else:
                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " failed to upload " + filename + " as the file was not found.\n")
                except Exception as e:
                    print(f"Error: {e}")

           # If the Client requests directory file list from the Server
            elif command == "/dir":
                try:
                    # Send the list of files to the client
                    if file_list:
                        connectionSocket.send(str(file_list).encode())
                    else:
                        connectionSocket.send("[]".encode())  # Send an empty list as a string

                    # Print on the server side
                    print("Device from port number " + str(addr[1]) + " requested the list of files in the server's working directory.\n")

                except Exception as e:
                    print(f"Error: {e}")

           # If the Client requests to fetch a file from the Server
            elif command == "/get":
                # Receive the filename from the client
                filename = connectionSocket.recv(1024).decode()

                try:
                    # Check if the file exists in the server
                    if filename not in file_list:
                        connectionSocket.send("Error: File not found in the server.".encode())

                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " requested " + filename + " from the server but the file was not found.\n")
                    else:
                        # Send the file size to the client
                        filesize = os.path.getsize(filename)
                        connectionSocket.send(str(filesize).encode())

                        # Read and send the file to the client in chunks
                        with open(filename, 'rb') as file:
                            while True:
                                file_data = file.read(1024)
                                if not file_data:
                                    break
                                connectionSocket.send(file_data)

                        connectionSocket.send(f"File received from Server: {filename}".encode())

                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " requested " + filename + " from the server.\n")

                except Exception as e:
                    print(f"Error: {e}")

            # If the Client sends a message to another Client
            elif command == "/send":
                # Receive the handle of the recipient
                recipient = connectionSocket.recv(1024).decode()

                try:
                    # Check if the recipient is registered
                    if recipient not in clients:
                        connectionSocket.send("False".encode())

                        connectionSocket.send("Error: Recipient not found.".encode())

                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " failed to send a message to " + recipient + " as the recipient was not found.\n")
                    else:
                        connectionSocket.send("True".encode())
                        message = connectionSocket.recv(1024).decode()
                        # Send the message to the recipient
                        clients[recipient]['socket'].send((handle + ": " + message).encode())
                        connectionSocket.send(("Message sent to " + recipient + ".").encode())
                        # Print on the server side
                        print("Device from port number " + str(addr[1]) + " sent a message to " + recipient + ".\n")

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

