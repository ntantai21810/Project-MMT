import socket
import threading
import getpass

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#If input password, don't show string when user type
inputPassword = 0

#Receive message from server and show to console
#If the message is {quit}, close the client
def receive():
    while True:
        try:
            message = client.recv(2048).decode()
            if message == "close":
                client.close()  
                break
            print(message)
        except:
            break

#Get message from user input and send to server
def send():
    global inputPassword
    while True:
        if inputPassword > 0:
            message = getpass.getpass("")
            inputPassword -= 1 
        else:
            message = input()
            #Handle input password
            if message.split()[0] == "login" or message.split()[0] == "register":
                inputPassword = 1
            if message.split()[0] == "change_password":
                inputPassword = 2
            if message.split()[0] == "upload":
                option = message.split()[1]
                if option != "change_name" and option != "multi_files":
                    client.sendall(bytes(message, "utf8"))
                    file = open("./client_files/" + option, "r")
                    while True:
                        data = file.read(2048)
                        if not data:
                            client.sendall(bytes(" ", "utf8"))
                            break
                        client.sendall(bytes(data, "utf8"))
                    file.close()
                    continue
        client.sendall(bytes(message, "utf8"))  
        if (message == "close"):
            break       

def connecToServer():
    while True:
        address = input("")
        if address.split()[0] != "connect":
            print("You must connect to server")
        else:
            host = address.split()[1]
            port = address.split()[3]
            client.connect((host, int(port)))
            return

# connecToServer()
host = "10.126.0.214"
port = 8080
client.connect((host, int(port)))
threading.Thread(target=receive).start()
threading.Thread(target=send).start()