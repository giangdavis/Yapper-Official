# Contains the Server, User, Room, & Lobby classes
import socket, re, select
import re
import select

PORT = 55555
MAX_MESSAGE_LENGTH = 4096
MAX_CLIENTS = 15
''' TO DO :  
Server disconnecting from clients 
Client/Server "gracefully" handling crashes 
? Password ? 
Extra credit: PMs, File Transfer 
join room command: check if user is already in room ?
cancel button in 'welcome menu lobby'
cancel button in 'list members' 
'''
# COMMAND STRINGS
# ===========================================================================
'''
COMMANDS = "All available commands:\n" + 
NAMECHANGE + 
NEWROOM + LEAVE 
MEMBERS
ROOMS
COMMAND 
CHATIN
'''


# ===========================================================================
# ===========================================================================
# ===========================================================================
# ===========================================================================

class User:
    def __init__(self, socket, name):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.rooms = {}  # {RoomName : Bool} Bool = user is sending msgs to room

    # ===========================================================================

    def __del__(self):
        self.name = ""
        self.socket.close()

    # ===========================================================================

    def setName(self, newName):
        self.name = newName

    # ===========================================================================

    def fileno(self):
        return self.socket.fileno()

    # ===========================================================================

    def getName(self):
        return self.name

    # ===========================================================================

    def addRoom(self, room):
        self.rooms[room] = True

    # ===========================================================================

    def printRooms(self):
        for x in self.rooms:
            print(x.name)

    # ===========================================================================

    def leaveRoom(self, roomName):
        self.rooms.pop(roomName)


# ===========================================================================
# ===========================================================================

class Room:
    def __init__(self, name, password=""):
        self.users = []  # a list of sockets
        self.name = name
        self.password = password

    # ===========================================================================

    def addUser(self, user):
        self.users.append(user)

    # ===========================================================================

    def printUsers(self):  # for server use only
        print("Users in room: " + self.name + " ")
        for x in self.users:
            print(x.getName() + ' ')

    # ===========================================================================

    def broadcast(self, msg):
        for x in self.users:
            x.socket.sendall(msg.encode())

    # ===========================================================================

    def removeUser(self, user):
        self.users.remove(user)

    # ===========================================================================

    def printMembers(self, user):  # to send the client users of room
        for x in self.users:
            member = x.name
            user.socket.sendall(member.encode())


# ===========================================================================
# ===========================================================================
# ===========================================================================
# ===========================================================================

class Lobby:
    def __init__(self):
        self.rooms = {}  # {room name : room}
        self.users = []  # users in lobby

    # ===========================================================================

    def newUser(self, name, user):
        prefix = ""
        user.setName(name)
        self.users.append(name)
        print("New user: " + user.name)
        if self.checkLobby() == False:
            prefix = "empty"
        msg = prefix + " !@#$Username!@#$"
        user.socket.sendall(msg.encode())

    # ===========================================================================

    def invalidCommand(self, user):
        user.socket.sendall(b'Invalid command')

    # ===========================================================================

    def promptForName(self, user):
        user.socket.sendall(b'You have successfully connected to the Lobby!!! What is your name?\n')

    # ===========================================================================

    def printRooms(self):
        print("Rooms: ")
        for x in self.rooms.values():
            print(x.name + " ")

    # ===========================================================================

    def checkLobby(self):
        if len(self.rooms) == 0:
            return False
        return True

    # ===========================================================================

    def listRooms(self, user):
        if len(self.rooms) == 0:  # no rooms to list:
            user.socket.sendall(b'!!!!!norooms@!@!@!')
        else:
            prefix = "listOfRooms!!@! "
            msg2 = ""
            for room in self.rooms:
                msg = room
                msg2 = msg2 + " " + msg

            finalMsg = prefix + msg2
            user.socket.sendall(finalMsg.encode())

    # ===========================================================================

    def disconnectUser(self, user):
        for roomName in user.rooms:
            room = self.rooms[roomName]
            room.removeUser(user)
        if user.name in self.users:
            self.users.remove(user.name)

    # ===========================================================================

    def addRoom(self, name, user):
        newRoom = Room(name)
        newRoom.addUser(user)
        self.rooms[name] = newRoom
        # print(self.rooms.get(name).name + "!!!!") print room
        user.addRoom(name)
        welcome = user.name + " has joined the room!\n"
        print(user.name + " created a new room")
        msg = "You will now receive messages from room (" + name + "), click chat to start chatting here"
        user.socket.sendall(msg.encode())

    # ===========================================================================

    def handle(self, user, msg):
        msgLen = len(re.findall(r'\w+', msg))  # returns an int
        msgArr = msg.split(" ")  # returns a list
        commandLen = len(msgArr[0])  # length of "$usersommand"
        print("command length = " + str(commandLen))
        print("msg length = " + str(msgLen))

        if "$newuser" in msg and commandLen == 8:
            if msgLen == 2:
                if msgArr[1] in self.users:
                    user.socket.sendall(b'$#@!Username$#@!')  # not success
                else:
                    self.newUser(msgArr[1], user)
            else:  # invalid arguments
                user.socket.sendall(b'$#@!Username$#@!')

                # elif "$commands" in msg and commandLen == 9:
            # user.socket.sendall(COMMANDS.encode())

        elif "$rooms" in msg and commandLen == 6:
            if msgLen == 1:
                self.listRooms(user)
            else:
                self.invalidCommand(user)

        elif "$room" in msg and commandLen == 5:  # cases : no room, existing room, existing room and user is already in there
            # how many rooms is the users trying to join ?
            # join rooms that exist and create rooms that don't
            # TODO shorten, optimize this code.
            if msgLen == 2:  # argument check
                # See if there is an existing room
                roomName = msgArr[1]
                print("Looking for room: " + roomName)
                if roomName in self.rooms:  # trying to join an existing room
                    print("check")
                    room = self.rooms[roomName]
                    if user in room.users:  # user is already in the room
                        user.socket.sendall(b"You're already in this room!\n")
                    else:
                        room.addUser(user)
                        room.printUsers()
                        user.addRoom(roomName)
                        welcome = user.name + " is now lurking. \n"
                        room.broadcast(welcome)
                        roomMsg = 'You have joined ' + roomName + '!'
                        user.socket.sendall(roomMsg.encode())
                else:  # new room TO DO turn into function
                    self.addRoom(roomName, user)
            elif msgLen > 2:  # user is trying to join multiple rooms
                for currentRoomName in msgArr[1:]:
                    print (currentRoomName)
                    if currentRoomName in self.rooms:
                        room = self.rooms[currentRoomName]
                        welcome = user.name + ":has joined the room!\n"
                        room.broadcast(welcome)
                        user.socket.sendall(
                            b'You now receive messages from this room, to chat in this room: use the command $chat\n')
                    else:
                        newRoom = Room(currentRoomName)
                        newRoom.addUser(user)
                        self.rooms[currentRoomName] = newRoom
                        print("created a new room:" + currentRoomName)
                        newRoom.printUsers()
                        user.socket.sendall(
                            b'You now receive messages from this room, to chat in this room: use the command $chat\n')
            else:
                user.socket.sendall(b'Room Join/Create failed. Try Again.')

        elif "$sendall" in msg and commandLen == 8:  # broadcast to all current rooms
            if msgLen > 1:
                newMsg = msg[9:] + "\n"
                for currentRoom in user.rooms:
                    if currentRoom in self.rooms:
                        self.rooms[currentRoom].broadcast(newMsg)

        elif "$leave" in msg and commandLen == 6:
            if msgLen == 2:
                roomName = msgArr[1]
                if roomName in self.rooms:  # found the room user is trying to leave
                    room = self.rooms[roomName]  # grab the room
                    room.removeUser(user)  # remove user from the room
                    user.leaveRoom(roomName)  # remove room from the user
                    if len(room.users) == 0:  # room is now empty, remove from rooms
                        print("before pop")
                        self.rooms.pop(roomName)
                    else:
                        room.broadcast(user.name + " has left the room\n")
            else:
                self.invalidCommand(user)

        elif "$members" in msg and commandLen == 8:
            if msgLen == 1:
                #roomName = msgArr[1]
                #if roomName in self.rooms:
                #room = self.rooms[roomName]
                #room.printMembers(user)
                #else:
                #self.invalidCommand(user)

                for userRoom in user.rooms:
                 if user.rooms[userRoom]:
                     member = user.name + " "
                     user.socket.sendall(member.encode())

            else:
                self.invalidCommand(user)

        elif "$exit" in msg and commandLen == 6:
            if msgLen == 1:
                if len(user.rooms) > 0:
                    for currentRoomName in user.rooms:  # go through the rooms the user is in
                        # remove user from the room
                        if currentRoomName in self.rooms:
                            room = self.rooms[currentRoomName]
                            room.removeUser(user)
                            if len(room.users) == 0:
                                self.rooms.pop(currentRoomName)  # check if room is empty, turn this into func
                                print("room: " + currentRoomName + " is empty, closing it off.\n")
                            else:
                                room.broadcast(user.name + " has left the room\n")
                user.socket.sendall(b'$exit')
            else:
                self.invalidCommand(user)

        else:
            if len(self.rooms) == 0:  # no rooms
                self.invalidCommand(user)
            else:
                for i in user.rooms:  # loop through the rooms that the user is in
                    if user.rooms.get(i):  # the user is actively chatting in this room
                        room = self.rooms.get(i)
                        msg2 = user.name + ": " + msg
                        room.broadcast(msg2)


# ===========================================================================
# ===========================================================================
# ===========================================================================
# ===========================================================================

class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socketList = []
        self.socketList.append(self.socket)

    def addClient(self):
        newSocket, addr = self.socket.accept()
        newUser = User(newSocket, "")
        # newUser.fileno()
        self.socketList.append(newUser)
        return newUser

    # ===========================================================================

    def run(self, ip):
        lobby = Lobby()
        self.socket.bind((ip, PORT))  # local host
        # s.bind((socket.gethostname(), chatClasses.PORT))
        self.socket.listen(MAX_CLIENTS)

        print("Server set up & listening! Connect with address: ", ip)

        while True:
            readables, _, _ = select.select(self.socketList, [], [])
            for notifiedSocket in readables:
                if notifiedSocket is self.socket:  # new connection
                    newUser = self.addClient()
                    lobby.promptForName(newUser)
                else:
                    try:
                        encodedMsg = notifiedSocket.socket.recv(MAX_MESSAGE_LENGTH)
                        msg = encodedMsg.decode()
                        if encodedMsg:  # msg from client
                            print("Received data from " + notifiedSocket.name + ": " + msg)
                            lobby.handle(notifiedSocket, msg.lower())
                        else:  # recv got 0 bytes, closed connection
                            print("Client sent 0 bytes, closed connection")
                            if notifiedSocket in self.socketList:
                                self.socketList.remove(notifiedSocket)
                                lobby.disconnectUser(notifiedSocket)
                                del notifiedSocket
                    except:
                        print("Connection to client has been broken")
                        lobby.disconnectUser(notifiedSocket)
                        self.socketList.remove(notifiedSocket)
                        del notifiedSocket

# ===========================================================================