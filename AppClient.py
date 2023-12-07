from socket import *
import os                  # for file size
import re                  # for regex
import threading
import time                # used to add slight delay after functions (to improve flow)

# Global Variables
handle = None              # stores the handle/alias
connected = False          # checks whether Client is connected to Server
clientSocket = None        # refers to the socket that connects the Client to the Server

# List of commands
commands = ["/join", "/leave", "/register", "/store", "/dir", "/get", "/?"]

# List of commands with paramters
paramCommands = [re.compile(r'^/join\s+((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|localhost)\s+(\d+)$'),
                 re.compile(r'^/register\s+(\S+)$'),
                 re.compile(r'^/store\s+(\S+)$'),
                 re.compile(r'^/get\s+(\S+)$')]

# Opening display function
def intro():
    print("------------------------------------")
    print("Welcome to the File Exchange System!")
    print("------------------------------------")
    print("Input '/?' to display list of commands.")
    print("------------------------------------")

# Prompt Client to enter a command
def userInput():
    # If Client is not yet registered
    if not handle:
        return input("\n<Unregistered>: ")
    # If registered
    else:
        return input("\n"+handle+": ")

# Error: Due to command syntax
def doesCommandExist(inputCommand):
    # Goes through every possible string of /<command> to check
    for command in commands:
        if inputCommand == command:
            return True
    print("Error: Command not found.")
    return False

# Error: Command parameters do not match or is not allowed:
def doesParamMatch(inputSyntax):
    # Skip if command does not have parameters
    if inputSyntax in ["/leave", "/dir", "/?"]:
        return True
    # If there are, check if it follows expected pattern (like /register <handle>)
    else:
        for command in paramCommands:
            # Uses regex to check if pattern exists
            match = re.match(command, inputSyntax)
            if match:
                return True
    print("Error: Command parameters do not match or is not allowed.")
    return False

# /?: Request command help to output all Input Syntax commands for references
def displayCommands():
    print("\n------------------------------------")
    print("List of Commands")
    print("------------------------------------")
    print("Connect to the server application:")
    print("Syntax: /join <server_ip_add> <port>")
    print("Sample: /join 192.168.1.1 12345")
    print("------------------------------------")
    print("Disconnect to the server application:")
    print("Syntax: /leave")
    print("------------------------------------")
    print("Request a unique handle or alias:")
    print("Syntax: /register <handle>")
    print("Sample: /register User1")
    print("------------------------------------")
    print("Send file to server:")
    print("Syntax: /store <filename>")
    print("Sample: /store Hello.txt")
    print("------------------------------------")
    print("Request directory file list from a server:")
    print("Syntax: /dir")
    print("------------------------------------")
    print("Fetch a file from a server:")
    print("Syntax: /get <filename>")
    print("Sample: /get Hello.txt")
    print("------------------------------------")
    print("Request command help to output all Input Syntax commands for references:")
    print("Syntax: /?")
    print("------------------------------------")

# /join <server_ip_add> <port>: Connect to the server application
def joinServer(inputs):
    # Global to ensure they retain/update overall value
    global clientSocket
    global connected

    # Get the server IP and port number
    serverName = inputs[1]  
    serverPort = int(inputs[2])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    
    # Connect to the server application
    try:
        clientSocket.connect((serverName, serverPort))
        connected = True
        # Uses threading to allow for concurrent functions
        threading.Thread(target=receiveMessage, args=(clientSocket,), daemon=True).start()
        time.sleep(1)
    
    # Message upon unsuccessful connection to the server due to the server not running or incorrect IP and Port combination
    except Exception:
        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")

# /leave: Disconnect to the server application
def leaveServer():
    # Global to ensure they retain/update overall value
    global connected
    global handle
    global clientSocket

    try:
        # Send "/leave" to Server
        clientSocket.send("/leave".encode())
        # Prints the response of the Server
        print(clientSocket.recv(1024).decode())
        time.sleep(1)
        # Closes the socket connecting Client to Server
        clientSocket.close()
        # Resets the connected and handle status
        connected = False
        handle = None
    except Exception:
        print("Error: Disconnection failed. Please connect to the server first.")

# /register <handle>: Register a unique handle or alias
def register(newHandle):
    # Global to ensure they retain/update overall value
    global handle

    try:
        # Send "/register" to Server
        clientSocket.send("/register".encode())
        # Send the handle/alias input to Server
        clientSocket.send(newHandle.encode())

        # Receive confirmation if the handle exists or not
        handleExists = clientSocket.recv(1024).decode()
        time.sleep(1)

        # Sets handle if allowed
        if handleExists == "False":
            handle = newHandle

        # Prints Server's comment on the registration
        print(clientSocket.recv(1024).decode())
        
    except Exception:
        print("Error: Registration failed.")

# /store <filename>: Send file to server
def storeFile(filename):
    # Global to ensure they retain/update overall value
    global clientSocket

    try:
        # Send "/store" to Server
        clientSocket.send("/store".encode())

        # Send the filename input to Server
        clientSocket.send(filename.encode())

        # Check if the file exists
        if not os.path.exists(filename):
            print("Error: File not found.")
        else:
            # Send the file size
            filesize = os.path.getsize(filename)
            clientSocket.send(str(filesize).encode())

            # Read and send the file to Server in chunks
            with open(filename, "rb") as file:
                while True:
                    file_data = file.read(1024)
                    if not file_data:
                        break
                    clientSocket.send(file_data)

            # Prints Server's comment on the file transfer
            print(clientSocket.recv(1024).decode())
    
    except Exception as e:
        print(f"Error: {e}")

# /dir: Request directory file list from the Server
def requestDir():
    # Global to ensure they retain/update overall value
    global clientSocket

    try:
        # Send "/dir" to Server
        clientSocket.send("/dir".encode())

        # Receive and print the list of files from the Server
        file_list = eval(clientSocket.recv(1024).decode())
        
        if not file_list:
            print("Server Directory is empty.")
        else:
            print("Server Directory")
            for file in file_list:
                print(file)

    except Exception as e:
        print(f"Error: {e}")

# /get <filename>: Fetch a file from the Server
def getFile(filename):
    # Global to ensure they retain/update overall value
    global clientSocket

    try:
        # Send "/get" to Server
        clientSocket.send("/get".encode())
        # Send the filename to Server
        clientSocket.send(filename.encode())

        # Receive the server's response
        response = clientSocket.recv(1024).decode()

        if response.startswith("Error"):
            print(response)
            return
        else:
            # Receive the file size from Server
            filesize = int(response)

            # Receive and save the file from Server
            with open(filename, 'wb') as file:
                totalRecv = 0
                while totalRecv < filesize:
                    data = clientSocket.recv(1024)
                    totalRecv += len(data)
                    file.write(data)

            # Prints Server's comment on the file transfer (excluding "OK" response)
            print(clientSocket.recv(1024).decode())

    except Exception as e:
        print(f"Error: {e}")

      
# Receiving messages 
def receiveMessage(clientSocket):
    try:
        # Takes the response from the Server
        data = clientSocket.recv(1024)
        print(data.decode())
    except Exception as e:
        print(f"Error: {e}")

# Main
def main():
    # Set following variables as global
    global handle
    global connected
    global clientSocket
    intro()

    while True:
        # Stores the entire command
        inputSyntax = userInput()
        # Contains the splitted command
        inputs = inputSyntax.split(' ')

        # Checks first if the syntax is valid, then leads to the functions
        if doesCommandExist(inputs[0]) and doesParamMatch(inputSyntax):
            if inputSyntax == "/?":
                displayCommands()

            elif inputs[0] == "/join":
                if connected:
                    print("Error: User is already connected to the server.")
                else:
                    joinServer(inputs)
                    
            elif inputSyntax == "/leave":
                leaveServer()

            elif inputs[0] == "/register":
                if connected and not handle:
                    register(inputs[1])
                elif connected and handle:
                    print("Error: User is already registered.")  
                else:
                    print("Error: User must be connected to the server.")

            elif inputs[0] == "/store":
                if connected and handle:
                    storeFile(inputs[1])
                elif connected and not handle:
                    print("Error: User must be registered.")
                else:
                    print("Error: User must be connected to the server.")

            elif inputSyntax == "/dir":
                if connected and handle:
                    requestDir()
                elif connected and not handle:
                    print("Error: User must be registered.")
                else:
                    print("Error: User must be connected to the server.")   

            elif inputs[0] == "/get":
                if connected and handle:
                    getFile(inputs[1])
                elif connected and not handle:
                    print("Error: User must be registered.")
                else:
                    print("Error: User must be connected to the server.")        

# Executable
main()