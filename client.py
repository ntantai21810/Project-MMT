import socket
import threading
import getpass
import os
from key import encrypt_message
from key import decrypt_message

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#If input password, don't show character when user type
inputPassword = 0

isReceived = True
isChatting = False
#Receive message from server and show to console
#If the message is close, close the client
def receive():
    global isReceived
    global isChatting
    while True:
        try:
            message = client.recv(2048).decode()
            #Close the connection
            if message == "close":
                client.close()  
                break
            #Send 1 file successfull, use in send multi file
            if message == "Done":
                isReceived = True
                continue
            #Client receive file from server
            if message.split()[0] == "_sendfile":
                content = ""
                filename = message.split()[1]
                while True:
                    data = client.recv(2048).decode()
                    if data == " ":
                        client.sendall(bytes("_done", "utf8"))
                        break
                    check = data[:4]
                    length = len(data)
                    if check == "b'gA" and length > 100:
                        encrypt_data = bytes(data[2:length-1],"utf8")
                        data = decrypt_message(encrypt_data)
                    content += data
                file = open("./client_files/" + filename, "x")
                file.close()
                file = open("./client_files/" + filename, "w")
                file.write(content)
                file.close()
                continue
            #Client receive multi file from server
            if message.split()[0] == "_send_multi_files":
                allFiles = message.split()[1:]
                for filename in allFiles:
                    content = ""
                    while True:
                        data = client.recv(2048).decode()
                        if data == " ":
                            # client.sendall(bytes("_done", "utf8"))
                            break
                        check = data[:4]
                        length = len(data)
                        if check == "b'gA" and length > 100:
                            encrypt_data = bytes(data[2:length-1],"utf8")
                            data = decrypt_message(encrypt_data)
                        content += data
                    file = open("./client_files/" + filename, "x")
                    file.close()
                    file = open("./client_files/" + filename, "w")
                    file.write(content)
                    file.close()
                    client.sendall(bytes("Done", "utf8"))
                continue
            if message == "_chat":
                isChatting = True
                client.sendall(bytes("_onchat", "utf8"))
                os.system("cls")
                continue
            print(message)
        except:
            break

#Get message from user input and send to server
def send():
    global inputPassword
    global isChatting
    while True:
        if inputPassword > 0:
            message = getpass.getpass("")
            check = input("Do you want to encrypt message before sending? (Y/N): ")
            if check == "Y":
                message = str(encrypt_message(message))
            inputPassword -= 1 
        else:
            message = input()
            #Handle input password
            if isChatting:
                if message == "_exit":
                    isChatting = False   
                client.sendall(bytes("_c" + message, "utf8"))
                continue
            if message.split()[0] == "login" or message.split()[0] == "register":
                inputPassword = 1
            if message.split()[0] == "change_password":
                inputPassword = 2
            if message.split()[0] == "download":
                check = input("Do you want to encrypt message before sending? (Y/N): ")
                if check == "Y":
                    message = "_y" + message
            if message.split()[0] == "upload":
                option = message.split()[1]
                check = input("Do you want to encrypt message before sending? (Y/N): ")
                if option != "change_name" and option != "multi_files":
                    client.sendall(bytes(message, "utf8"))
                    file = open("./client_files/" + option, "r")
                    while True:
                        data = file.read(2048)
                        if not data:
                            client.sendall(bytes(" ", "utf8"))
                            break
                        if check == "Y":
                            data = str(encrypt_message(data))
                        client.sendall(bytes(data, "utf8"))
                    file.close()
                    continue
                if option == "multi_files":
                    client.sendall(bytes(message, "utf8"))
                    allFiles = message.split()[2:]
                    global isReceived
                    for fileName in allFiles:
                        file = open("./client_files/" + fileName, "r")
                        while True:
                            if isReceived:
                                data = file.read(2048)
                                if not data:
                                    client.sendall(bytes(" ", "utf8"))
                                    break
                                if check == "Y":
                                    data = str(encrypt_message(data))
                                client.sendall(bytes(data, "utf8"))
                        isReceived = False
                        file.close()
                    continue
            if message.find("create") != -1:
                isChatting = True
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
host = "192.168.1.3"
port = 8080
client.connect((host, int(port)))

receiveThread = threading.Thread(target=receive).start()

sendThread = threading.Thread(target=send).start()