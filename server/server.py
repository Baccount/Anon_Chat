import threading
import json
import os
from cmd import Cmd
from onion_tor import CreateOnion

class Server(Cmd):
    """
    Server Class
    """
    prompt = ''
    intro = '[Welcome] Server Operator \n'

    def __init__(self):
        """
        structure
        """
        super().__init__()
        # CreateOnion Tor Onion instance
        self.tor = CreateOnion()
        self.__connections = list()
        self.__nicknames = list()
        self.__lock = threading.Lock()

    def do_ban(self, args):
        """
        Ban a user from the chat room.

        :param args: The id of the user to be banned.
        """
        try:
            if int(args) == 0:
                print('Cannot ban server because it is the server!')
                return
            self.ban_user(user_id=int(args))
        except Exception as e:
            print('server line 38')
            print(e)

    def do_l(self, args):
        """
        List all users in the chat room.

        """
        try:
            for i in range(len(self.__connections)):
                print(f'{i} : {self.__nicknames[i]}')
        except Exception as e:
            print('server line 51')
            print(e)


    def do_s(self, args):
        """
        Send a message to the chat room from the Server.

        :param args: The message to be sent.
        """
        args = '\033[92m' + args + '\033[0m'
        self.__broadcast(user_id=0 ,message=args)


    def ban_user(self, user_id):
        """
        Ban a user from the chat room.

        Args:
        - user_id (int): The ID of the user to be banned.
        """
        try:
            nickname = self.__nicknames[user_id]
            self.__broadcast(message=f"User {nickname}({user_id}) has been banned from the chat room")
            self.__connections[user_id].close()
            # remove the user from the list
            self.__connections[user_id] = None
            self.__nicknames[user_id] = None
        except Exception as e:
            print('server line 81')
            print(e)



    def disconnectUsr(self, user_id, nickname="NONE"):
        """
        Disconnect a user from the chat room.

        Args:
        - user_id (int): The ID of the user to be disconnected.
        - nickname (str, optional): The nickname of the user. Default is "NONE".
        """
        try:
            print('[Server] user', user_id, nickname, 'exit chat room')
            self.__connections[user_id].close()
            # remove the user from the list
            self.__connections[user_id] = None
            self.__nicknames[user_id] = None
        except Exception as e:
            print('server line 77')
            print(e)



    def separateJson(self, buffer):
        """
        Separate a buffer of text into individual JSON objects.

        :param buffer: A string buffer containing one or more JSON objects.
        :return: A list of strings, each representing a separate JSON object.
        """
        objects = []
        start = 0
        end = buffer.find('{', start)
        while end != -1:
            start = end
            count = 1
            end = start + 1
            while count > 0 and end < len(buffer):
                if buffer[end] == '{':
                    count += 1
                elif buffer[end] == '}':
                    count -= 1
                end += 1
            objects.append(buffer[start:end])
            start = end
            end = buffer.find('{', start)
            # Process each JSON object
            print(f'objects {objects}')
            return objects




    def decode_buffer(self, buffer):
        return buffer.decode()


    def handle_obj(self, obj, user_id, nickname):
        if obj['type'] == 'broadcast':
            self.__broadcast(obj['sender_id'], obj['message'])
        elif obj['type'] == 'logout':
            self.__broadcast(message=f'user {nickname} ({user_id}) has exited the chat room')
            self.disconnectUsr(user_id, nickname)
        else:
            print('server line 96')
            self.disconnectUsr(user_id, nickname)

    def __user_thread(self, user_id):
        """
        user thread
        :param user_id: user id
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print(f'[Server] user {user_id} ({nickname}) joined the chat room')

        while True:
            try:
                buffer = b''
                chunk = connection.recv(1024)
                print(f"chunk: {chunk}")

                if chunk:
                    buffer += chunk
                else:
                    self.disconnectUsr(user_id, nickname)
                    break

                buffer = self.decode_buffer(buffer)
                print(f"buffer: {buffer}")

                objects = self.separateJson(buffer)

                for obj in objects:
                    if obj:
                        obj = json.loads(obj)
                        self.handle_obj(obj, user_id, nickname)
            except Exception as e:
                print('server line 177')
                print(e)
                self.disconnectUsr(user_id, nickname)
                break


    def __broadcast(self, user_id=0, message=''):
        """
        broadcast
        :param user_id: user id (0 is the system)
        :param message: broadcast content
        """
        # Acquire the lock to prevent multiple broadcasts from running simultaneously
        self.__lock.acquire()
        try:
            for i in range(len(self.__connections)):
                if user_id != i and self.__connections[i]:
                    self.__connections[i].send(json.dumps({
                        'sender_id': user_id,
                        'sender_nickname': self.__nicknames[user_id],
                        'message': message
                    }).encode())
        finally:
            # Release the lock after the broadcast has finished
            self.__lock.release()

    def __waitForLogin(self, connection):
        """
        Wait for a client to log in and start a new thread for the client.

        :param connection: The connection with the client.
        """
        try:
            while True:
                buffer = connection.recv(1024).decode()
                print(buffer)
                obj = json.loads(buffer)
                if obj['type'] == 'login':
                    # check if the nickname is already in use
                    if obj['nickname'] in self.__nicknames:
                        connection.send(json.dumps({
                            'id': -1
                        }).encode())
                        continue
                    # add the connection and nickname to the lists
                    self.__connections.append(connection)
                    self.__nicknames.append(obj['nickname'])
                    connection.send(json.dumps({
                        'id': len(self.__connections) - 1
                    }).encode())
                    # start a new thread for the user
                    thread = threading.Thread(target=self.__user_thread, args=(len(self.__connections) - 1,))
                    thread.setDaemon(True)
                    thread.start()
                    break

        except Exception as e:
            print('Client Disconnected, server line 158')
            print(e)
            connection.close()






    def delete_private_key(self):
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')
        if os.path.exists(key_path):
            os.remove(key_path)
            print("Private key deleted")

    def start(self):
        """
        Start the server and listen for incoming connections.
        """
        print("Do you want to CreateOnion an ephemeral or non-ephemeral hidden service?")
        print("1. Ephemeral")
        print("2. Non-ephemeral")
        print("3. Delete private key")
        choice = input("Enter choice: ")
        if choice == "1":
            response = self.tor.ephemeral_onion()
        elif choice == "2":
            response = self.tor.non_ephemeral_onion()
        elif choice == "3":
            self.delete_private_key()
            exit()


        print('[Server] server is running......')
        print(f"Onion Service: {response.service_id}.onion")


        self.__connections.append(None)
        self.__nicknames.append('\033[92m' + 'Server' + '\033[0m')

        cmdThread = threading.Thread(target=self.cmdloop)
        cmdThread.setDaemon(True)
        cmdThread.start()
        while True:
            connection, address = self.tor.socket.accept()
            print('[Server] received a new connection', connection.getsockname(), connection.fileno())

            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()
