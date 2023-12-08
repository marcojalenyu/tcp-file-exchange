from socket import *
from tkinter import scrolledtext
import tkinter as tk       # for GUI
import os                  # for file size
import re                  # for regex
import threading
import struct
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

# GUI class
class gui:
    def __init__(self, master):
        self.master = master
        self.master.title("File Exchange System")
        self.master.geometry("600x450")

        # Create a text widget for displaying messages
        self.chat_text = tk.Text(self.master, wrap=tk.WORD, width=60, height=20, state=tk.DISABLED)
        self.chat_text.grid(row=0, column=0, padx=10, pady=10)

        # Configure tags for message alignment
        self.chat_text.tag_configure('user', justify='right')
        self.chat_text.tag_configure('other', justify='left')

        # Create a scrollbar for the text widget
        self.scrollbar = tk.Scrollbar(self.master, command=self.chat_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.chat_text['yscrollcommand'] = self.scrollbar.set

        # Create an entry widget for typing messages
        self.message_entry = tk.Entry(self.master, width=50)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)

        # Create a button to send messages
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Create a label to display user information
        self.user_label = tk.Label(self.master, text="User: Not Connected", anchor=tk.W)
        self.user_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Bind the Enter key to the send_message method
        self.master.bind('<Return>', lambda event: self.send_message())

        # Display the intro message
        self.display_intro()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.display_message(f"You:\n{message}\n", is_user_message=True)
            self.process_user_input(message)
            self.message_entry.delete(0, tk.END)

    def process_user_input(self, user_input):
        # Contains the splitted command
        inputs = user_input.split(' ')

        # Checks first if the syntax is valid, then leads to the functions
        if doesCommandExist(inputs[0], self) and doesParamMatch(user_input, self):

            if user_input == "/?":
                displayCommands(self)

            elif inputs[0] == "/join":
                if connected:
                    self.display_message("Error: User is already connected to the server.\n", is_user_message=False)
                else:
                    joinServer(inputs, self)
                    
            elif user_input == "/leave":
                leaveServer(self)

            elif inputs[0] == "/register":
                if connected and not handle:
                    register(inputs[1], self)
                elif connected and handle:
                    self.display_message("Error: User is already registered.\n", is_user_message=False)  
                else:
                    self.display_message("Error: User must be connected to the server.\n", is_user_message=False)

            elif inputs[0] == "/store":
                if connected and handle:
                    storeFile(inputs[1], self)
                elif connected and not handle:
                    self.display_message("Error: User must be registered.\n", is_user_message=False)
                else:
                    self.display_message("Error: User must be connected to the server.\n", is_user_message=False)

            elif user_input == "/dir":
                if connected and handle:
                    requestDir(self)
                elif connected and not handle:
                    self.display_message("Error: User must be registered.\n", is_user_message=False)
                else:
                    self.display_message("Error: User must be connected to the server.\n", is_user_message=False)

            elif inputs[0] == "/get":
                if connected and handle:
                    getFile(inputs[1], self)
                elif connected and not handle:
                    self.display_message("Error: User must be registered.\n", is_user_message=False)
                else:
                    self.display_message("Error: User must be connected to the server.\n", is_user_message=False)

    def display_message(self, message, is_user_message=True):
        # Set state to normal to modify the text widget
        self.chat_text.config(state=tk.NORMAL)

        # Determine the tag for the message based on alignment
        tag = 'user' if is_user_message else 'other'

        # Insert the message with the specified tag
        self.chat_text.insert(tk.END, message, tag)
        self.chat_text.insert(tk.END, '\n')  # Add a newline after each message

        # Disable the text widget again
        self.chat_text.config(state=tk.DISABLED)

        # Scroll to the end
        self.chat_text.see(tk.END)

    def update_user_label(self, user_info):
        self.user_label.config(text=f"User: {user_info}")

    # Opening display function
    def display_intro(self):
        intro = "Welcome! Input '/?' to display list of commands.\n"
        self.display_message(intro, is_user_message=False)

# Error: Due to command syntax
def doesCommandExist(inputCommand, gui):
    # Goes through every possible string of /<command> to check
    for command in commands:
        if inputCommand == command:
            return True
    gui.display_message("Error: Command not found.\n", is_user_message=False)
    return False

# Error: Command parameters do not match or is not allowed:
def doesParamMatch(inputSyntax, gui):
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
    gui.display_message("Error: Command parameters do not match or is not allowed.\n", is_user_message=False)
    return False

# /?: Request command help to output all Input Syntax commands for references
def displayCommands(gui):
    gui.display_message("List of Commands:", is_user_message=False)
    gui.display_message("/join <server_ip_add> <port>", is_user_message=False)
    gui.display_message("/leave", is_user_message=False)
    gui.display_message("/register <handle>", is_user_message=False)
    gui.display_message("/store <filename>", is_user_message=False)
    gui.display_message("/dir", is_user_message=False)
    gui.display_message("/get <filename>", is_user_message=False)
    gui.display_message("/?\n", is_user_message=False)

# /join <server_ip_add> <port>: Connect to the server application
def joinServer(inputs, gui):
    # Global to ensure they retain/update overall value
    global clientSocket
    global connected
    
    # Connect to the server application
    try:
        # Get the server IP and port number
        serverName = inputs[1]  
        serverPort = int(inputs[2])
        clientSocket = socket(AF_INET, SOCK_STREAM)
        # Connect to the server
        clientSocket.connect((serverName, serverPort))
        connected = True
        # Uses threading to allow for concurrent functions
        threading.Thread(target=receiveMessage, args=(clientSocket, gui), daemon=True).start()
        time.sleep(1)

        gui.update_user_label("Unregistered")
    
    # Message upon unsuccessful connection to the server due to the server not running or incorrect IP and Port combination
    except Exception:
        gui.display_message("Error: Connection to the Server has failed! Please check IP Address and Port Number.\n", is_user_message=False)

# /leave: Disconnect to the server application
def leaveServer(gui):
    # Global to ensure they retain/update overall value
    global connected
    global handle
    global clientSocket

    try:
        # Send "/leave" to Server
        clientSocket.send("/leave".encode())
        # Prints the response of the Server
        gui.update_user_label("Not Connected")
        gui.display_message(clientSocket.recv(1024).decode(), is_user_message=False)
        time.sleep(1)
        # Closes the socket connecting Client to Server
        clientSocket.close()
        # Resets the connected and handle status
        connected = False
        handle = None

    except Exception:
        gui.display_message("Error: Disconnection failed. Please connect to the server first.\n", is_user_message=False)

# /register <handle>: Register a unique handle or alias
def register(newHandle, gui):
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
            gui.update_user_label(handle)

        # Prints Server's comment on the registration
        gui.display_message(clientSocket.recv(1024).decode(), is_user_message=False)
        
    except Exception:
        gui.display_message("Error: Registration failed.\n", is_user_message=False)

# /store <filename>: Send file to server
def storeFile(filename, gui):
    # Global to ensure they retain/update overall value
    global clientSocket

    try:
        # Send "/store" to Server
        clientSocket.send("/store".encode())

        # Send the filename input to Server
        clientSocket.send(filename.encode())

        # Check if the file exists
        if not os.path.exists(filename):
            gui.display_message("Error: File not found.\n", is_user_message=False)
        else:
            # Send the file size
            filesize = os.path.getsize(filename)
            clientSocket.send(struct.pack("!Q", filesize))
            buffer = 4096

            # Read and send the file to Server in chunks
            with open(filename, 'rb') as file:
                while True:
                    file_data = file.read(buffer)
                    if not file_data:
                        break
                    clientSocket.sendall(file_data)
                    buffer = min(2 * buffer, filesize - file.tell())

            # Prints Server's comment on the file transfer
            gui.display_message(clientSocket.recv(1024).decode(), is_user_message=False)
    
    except Exception as e:
        gui.display_message(f"Error: {e}\n", is_user_message=False)

# /dir: Request directory file list from the Server
def requestDir(gui):
    # Global to ensure they retain/update overall value
    global clientSocket

    try:
        # Send "/dir" to Server
        clientSocket.send("/dir".encode())

        # Receive and print the list of files from the Server
        file_list = eval(clientSocket.recv(1024).decode())
        
        if not file_list:
            gui.display_message("Server Directory is empty.\n", is_user_message=False)
        else:
            gui.display_message("Server Directory:", is_user_message=False)
            for file in file_list:
                gui.display_message(file, is_user_message=False)

    except Exception as e:
        gui.display_message(f"Error: {e}\n", is_user_message=False)

# /get <filename>: Fetch a file from the Server
def getFile(filename, gui):
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
            gui.display_message(response+"\n", is_user_message=False)
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
            gui.display_message(clientSocket.recv(1024).decode(), is_user_message=False)

    except Exception as e:
        gui.display_message(f"Error: {e}\n", is_user_message=False)

# Receiving messages 
def receiveMessage(clientSocket, gui):
    try:
        # Takes the response from the Server
        data = clientSocket.recv(1024)
        gui.display_message(data.decode()+"\n", is_user_message=False)
    except Exception as e:
        gui.display_message(f"Error: {e}\n", is_user_message=False)

"""
main(): This function implements the overall application.
"""
def main():
    # Set following variables as global
    global handle
    global connected
    global clientSocket

    # Creates the GUI window
    root = tk.Tk()
    window = gui(root)

    root.mainloop()

    while True:
        root.update_idletasks()
        root.update()
    
"""
Executable
"""
main()