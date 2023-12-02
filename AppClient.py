from socket import *
import re
import threading

# Global Variables
handle = None
connected = False

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

# Checks if there are any syntax/parameter error:
def isInputValid(inputSyntax, inputCommand):
    return doesCommandExist(inputCommand) and doesParamMatch(inputSyntax)

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

# Receiving messages 
def receiveMessage(clientSocket):
    try:
        data = clientSocket.recv(1024)
        print("Server:", data.decode())
    except Exception as e:
        print(f"Error receiving message: {e}")

# Main
def main():
    # Set following variables as global
    global handle
    global connected
    intro()

    while True:
        # Stores the entire command
        inputSyntax = userInput()
        # Contains the splitted command
        inputs = inputSyntax.split(' ')

        if isInputValid(inputSyntax, inputs[0]):
            # Get List of Commands
            if inputSyntax == "/?":
                displayCommands()

            # Get Server Address and Port Number
            elif inputs[0] == "/join":

                if connected:
                    print("Error: User is already connected to the server.")
                else:
                    serverName = inputs[1]
                    serverPort = int(inputs[2])
                    clientSocket = socket(AF_INET, SOCK_STREAM)
                    
                    # Connect to the server application
                    try:
                        clientSocket.connect((serverName, serverPort))
                        connected = True

                        # Message upon successful connection to the server
                        print("Connection to the File Exchange Server is successful!\n")

                        # For receiving upcoming messages
                        threading.Thread(target=receiveMessage, args=(clientSocket,), daemon=True).start()
                    
                    # Message upon unsuccessful connection to the server due to the server not running or incorrect IP and Port combination
                    except Exception:
                        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
            
            # Leave Server
            elif inputSyntax == "/leave":
                
                # Disconnect to the server application.
                if connected:
                    clientSocket.close()
                    # Reset the handle and set connection as False
                    connected = False
                    handle = None

                    # Message upon successful disconnection to the server
                    print("Connection closed. Thank you!")
                
                # Message upon unsuccessful disconnection to the server due to not currently being connected
                else:
                    print("Error: Disconnection failed. Please connect to the server first.")

# Executable
main()