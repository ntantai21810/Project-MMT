import socket
import threading
import os

#Store name of clients and address of clients
clients = {}
address = {}

usersOnline = []

host = "10.126.7.119"
port = 8080

#Create server socket and bind address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

#Accept connection from client and create thread for this connection
def acceptConnection():
    while True:
        connection, addr = server.accept()
        print(addr[0] + " has connected")
        address[connection] = addr[0]
        threading.Thread(target=handleClient, args=(connection,)).start()


#Handle connection
def handleClient(connection):
    hasLogin = False
    while True:
        message = connection.recv(2048).decode()
        #Handle login
        #Check if user isn't logged in
        #Check user name and password in database
        if message.split()[0] == "login":
            username = message.split()[1]
            connection.sendall(bytes("password", "utf8"))
            password = connection.recv(2048).decode()
            if (hasLogin):
                connection.sendall(bytes("You has already login", "utf8"))
            else:
                if authUser(username, password) == 0: 
                    welcomeMessage = "Welcome " + username +". If you want to exit type 'close'"
                    connection.sendall(bytes(welcomeMessage, "utf8"))
                    message = " has joined the chat room"
                    broadcast(message, connection)
                    clients[connection] = username
                    hasLogin = True
                    usersOnline.append(username)
                elif authUser(username, password) == 1:
                    connection.sendall(bytes("Wrong password", "utf8"))
                else:
                    connection.sendall(bytes("User name doesn't have in database", "utf8"))
        #Handle register
        #Get info from user
        #Check if user isn't logged in
        #Store info to database
        elif message.split()[0] == "register":
            username = message.split()[1]
            connection.sendall(bytes("password", "utf8"))
            password = connection.recv(2048).decode()
            connection.sendall(bytes("Date of birth: ", "utf8"))
            dateOfBirth = connection.recv(2048).decode()
            connection.sendall(bytes("Some note? (Press _b to blank) ", "utf8"))
            note = connection.recv(2048).decode()
            connection.sendall(bytes("Your nickname ", "utf8"))
            nickname = connection.recv(2048).decode()
            if (hasLogin):
                connection.sendall(bytes("You has already login", "utf8"))
            else:
                if (not hasInDatabase(username)):
                    writeToDatabase(username, password, dateOfBirth, note, nickname)
                    successfulMessage = "Register successful" + ". If you want to exit type 'close'"
                    connection.sendall(bytes(successfulMessage, "utf8"))
                    message = " has joined the chat room"
                    broadcast(message, connection)
                    clients[connection] = username
                    hasLogin = True
                    usersOnline.append(username)
                else:
                    connection.sendall(bytes("User has already exists", "utf8"))
        #Handle change password
        #Get username, old password, new password
        #Check if user is logged in
        #Check username in database, old password and new password is same
        #Store new info to database
        elif not hasLogin:
            connection.sendall(bytes("You must login", "utf8"))
        elif message.split()[0] == "change_password":
            username = message.split()[1]
            connection.sendall(bytes("password", "utf8"))
            password = connection.recv(2048).decode()
            connection.sendall(bytes("new password: ", "utf8"))
            newPassword = connection.recv(2048).decode()
            if authUser(username, password) == 0:
                changePassword(username, password, newPassword)
                connection.sendall(bytes("Change successfull", "utf8"))
            elif authUser(username, password) == 1:
                connection.sendall(bytes("Wrong password", "utf8"))
            else:
                connection.sendall(bytes("Username doesn't have in database", "utf8"))
        #Handle check user
        #Get option and print corresponding info 
        elif message.split()[0] == "check_user":
            option = message.split()[1]
            username = message.split()[2]
            if not hasInDatabase(username):
                connection.sendall(bytes("User doesn't have in databse"))
            elif option == "find":
                connection.sendall(bytes("User has in database", "utf8"))
            elif option == "online":
                if username in usersOnline:
                    connection.sendall(bytes("User is online", "utf8"))
                else:
                    connection.sendall(bytes("User is not online", "utf8"))
            elif option == "show_date":
                dateOfBirth = getDateOfBirth(username)
                connection.sendall(bytes(dateOfBirth, "utf8"))
            elif option == "show_fullname":
                fullname = getNickName(clients[connection])
                connection.sendall(bytes(fullname, "utf8"))
            elif option == "show_note":
                note = getNoteOfUser(username)
                connection.sendall(bytes(note, "utf8"))
            elif option == "show_all":
                info = username + " " + getDateOfBirth(username) + " " + getNoteOfUser(username)
                connection.sendall(bytes(info, "utf8"))
        #Handle setup info
        #Check if user is logged in
        #Get option, data and handle
        elif message.split()[0] == "setup_info":
            option = message.split()[1]
            data = message.split()[2]
            if option == "fullname":
                changeName(clients[connection], data)
                connection.sendall(bytes("Change successful", "utf8"))
                clients[connection] = data
            elif option == "date":
                changeDateOfBirth(clients[connection], data)
                connection.sendall(bytes("Change successful", "utf8"))
            elif option == "note":
                changeNote(clients[connection], data)
                connection.sendall(bytes("Change successful", "utf8"))
        elif message.split()[0] == "upload":
            option = message.split()[1]
            if option == "change_name" or option == "multi_files":
                newName = message.split()[2]
                oldName = message.split()[3]
                if option == "change_name":
                    os.rename("./server_files/" + oldName, "./server_files/" + newName)
                    connection.sendall(bytes("Change successfully", "utf8"))
                if option == "multi_files":
                    allFiles = message.split()[2:]
                    for fileName in allFiles:
                        content = ""
                        while True:
                            data =  connection.recv(2048).decode()
                            if (data == " "):
                                break
                            content += data
                        file = open("./server_files/" + fileName, "x")
                        file.close()
                        file = open("./server_files/" + fileName, "w")
                        file.write(content)
                        file.close()
                        connection.sendall(bytes("Done", "utf8"))
                    print("Receives files from " + clients[connection])
                    connection.sendall(bytes("Send successful", "utf8"))
            else:
                content = ""
                while True:
                    data =  connection.recv(2048).decode()
                    if (data == " "):
                        break
                    content += data
                file = open("./server_files/" + option, "x")
                file.close()
                file = open("./server_files/" + option, "w")
                file.write(content)
                file.close()
                print("Receive file from " + clients[connection])
                connection.sendall(bytes("Send successful", "utf8"))
        elif message.split()[0] == "download":
            option = message.split()[1]
            if option == "multi_files":
                print()
            else:
                if os.path.isfile("./server_files/" + option):
                    connection.sendall(bytes("_sendfile " + option, "utf8"))
                    file = open("./server_files/" + option, "r")
                    while True:
                        data = file.read(2048)
                        if not data:
                            connection.sendall(bytes(" ", "utf8"))
                            break
                        connection.sendall(bytes(data, "utf8"))
                    file.close()
                    connection.sendall(bytes("Receive successfull", "utf8"))
                else:
                    connection.sendall(bytes("File is not exist", "utf8"))
        else:
            connection.sendall(bytes("close", "utf8"))
            print(clients[connection] + " has left the room")
            connection.close()
            broadcast(clients[connection] + " has left the room", connection)
            usersOnline.remove(clients[connection])
            del clients[connection]
            del address[connection]
            break

#Notify to other clients
def broadcast(message, connection):
    for sock in clients:
        if sock != connection:
            sock.sendall(bytes(clients[connection] + ": " + message, "utf8"))

#Check username and password
# - 0: True
# - 1: Wrong password
# - 2: Don't have in database 
def authUser(username, password):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0] and password == user.split()[1]:
            return 0
        elif username == user.split(" ")[0] and password != user.split()[1]:
            return 1
    file.close()
    return 2

#Check if user has already in database
def hasInDatabase(username):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            return True
    file.close()
    return False

def getDateOfBirth(username):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            return user.split()[2]
    file.close()
    return ""

def getNoteOfUser(username):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            if (len(user.split()) < 4):
                return ""
            else:
                return user.split()[3]
    file.close()
    return ""

def getNickName(username):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    updatedUsers = ""
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            if len(user.split(" ")) <= 4:
                return user.split(" ")[3]
            else:
                return user.split(" ")[4]
    file.close()
    return ""

def writeToDatabase(username, password, dateOfBirth, note, nickname):
    file = open("./database.txt", "a")
    file.write(username)
    file.write(" ")
    file.write(password)
    file.write(" ")
    file.write(dateOfBirth)
    file.write(" ")
    if note != "_b":
        file.write(note)
        file.write(" ")
    file.write(nickname)
    file.write("\n")
    file.close()

def changePassword(username, password, newPassword):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    updatedUsers = ""
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            updatedUsers += user.replace(password, newPassword) + "\n"
        else:
            updatedUsers += user + "\n"
    file.close()
    file = open("./database.txt", "w")
    file.write(updatedUsers)
    file.close()

def changeName(username, nickname):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    updatedUsers = ""
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            if len(user.split(" ") <= 4):
                updatedUsers += user.replace(user.split(" ")[3], nickname)
            else:
                updatedUsers += user.replace(user.split(" ")[4], nickname)
                
        else:
            updatedUsers += user + "\n"
    file.close()
    file = open("./database.txt", "w")
    file.write(updatedUsers)
    file.close()

def changeDateOfBirth(username, date):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    updatedUsers = ""
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]:
            updatedUsers += user.replace(user.split()[2], date) + "\n"
        else:
            updatedUsers += user + "\n"
    file.close()
    file = open("./database.txt", "w")
    file.write(updatedUsers)
    file.close()

def changeNote(username, note):
    file = open("./database.txt", "r")
    allUsers = file.read().split("\n")
    updatedUsers = ""
    for user in allUsers:
        if user == "":
            break
        if username == user.split(" ")[0]: 
            if (len(user.split()) <= 4):
                updatedUsers += user.split(" ")[0] + " " + user.split(" ")[1] + " " + user.split(" ")[2] + " " + note + " " + user.split(" ")[3] + "\n"
            else:
                updatedUsers += user.replace(user.split()[3], note) + "\n"
        else:
            updatedUsers += user + "\n"
    file.close()
    file = open("./database.txt", "w")
    file.write(updatedUsers)
    file.close()

server.listen(5)
print("Waiting for connection...")
acceptThread = threading.Thread(target=acceptConnection)
acceptThread.start()
acceptThread.join() #Wait until thread terminate
server.close()