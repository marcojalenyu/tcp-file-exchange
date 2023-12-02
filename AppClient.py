from socket import *
import re
import threading
import time
# Global Variables
handle = None
connected = False
clientSocket = None

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

# Prompt User to enter a command
def userInput():
    if not handle:
        return input("\n<Unregisted>: ")
    else:
        return input("\n"+handle+": ")

# Error: Due to command syntax
def doesCommandExist(inputCommand):
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
    # If there are, check if it follows expected pattern
    else:
        for command in paramCommands:
            match = re.match(command, inputSyntax)
            if match:
                return True
    print("Error: Commmand paramters do not match or is not allowed.")
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
        threading.Thread(target=receiveMessage, args=(clientSocket,), daemon=True).start()
        time.sleep(1)
    
    # Message upon unsuccessful connection to the server due to the server not running or incorrect IP and Port combination
    except Exception:
        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")

# /leave: Disconnect to the server application
def leaveServer():
    global connected
    global handle
    try:
        clientSocket.send("/leave".encode())
        print(clientSocket.recv(1024).decode())
        time.sleep(1)
        clientSocket.close()
        connected = False
        handle = None
    except Exception:
        print("Error: Disconnection failed. Please connect to the server first.")

# Receiving messages 
def receiveMessage(clientSocket):
    try:
        data = clientSocket.recv(1024)
        print(data.decode())
    except Exception as e:
        print(f"Error receiving message: {e}")

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

# Executable
main()