import socket
import threading
import json
from stem.control import Controller
from random import randint
import os


class Server:
    """
    server class
    """

    def __init__(self):
        """
        structure
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connections = list()
        self.__nicknames = list()
        self.__lock = threading.Lock()

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

    def disconnectUsr(self, user_id, nickname):
        """
        disconnect User
        """
        print('[Server] user', user_id, nickname, 'exit chat room')
        print('server line 45')
        self.__connections[user_id].close()
        # remove the user from the list
        self.__connections[user_id] = None
        self.__nicknames[user_id] = None



    def __user_thread(self, user_id):
        """
        user thread
        :param user_id: user id
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] user', user_id, nickname, 'join the chat room')
        while True:
            try:
                buffer = b''
                chunk = connection.recv(1024)
                print(f"chunk: {chunk}")
                if chunk:
                    buffer += chunk
                else:
                    self.disconnectUsr(user_id, nickname)
                    # close the current thread
                    break
                # Decode the buffer into a string
                buffer = buffer.decode()
                print(f"buffer: {buffer}")
                # Split the buffer into individual JSON objects
                objects = self.separateJson(buffer)
                for obj in objects:
                    if obj:
                        # Parse the JSON object
                        obj = json.loads(obj)
                                # Broadcast message
                        if obj['type'] == 'broadcast':
                            self.__broadcast(obj['sender_id'], obj['message'])
                        elif obj['type'] == 'logout':
                            self.__broadcast(message='user ' + str(nickname) + '(' + str(user_id) + ')' + 'exit chat room')
                            self.disconnectUsr(user_id, nickname)
                            break
                        else:
                            print('server line 96')
                            self.disconnectUsr(user_id, nickname)
                            break
            except Exception as e:
                print('server line 97')
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
            for i in range(1, len(self.__connections)):
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




    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        port = randint(10000, 65535)
        controller = Controller.from_port(port = 9051)
        controller.authenticate()

        response = controller.create_ephemeral_hidden_service({80: port}, await_publication = True)
        print(f"Created new hidden service with onion address: {response.service_id}.onion")
        return port


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')
        port = randint(10000, 65535)
        controller = Controller.from_port(port = 9051)
        controller.authenticate()

        if not os.path.exists(key_path):
            service = controller.create_ephemeral_hidden_service({80: port}, await_publication = True)
            print("Started a new hidden service with the address of %s.onion" % service.service_id)
            with open(key_path, 'w') as key_file:
                key_file.write('%s:%s' % (service.private_key_type, service.private_key))
        else:
            with open(key_path) as key_file:
                key_type, key_content = key_file.read().split(':', 1)

            service = controller.create_ephemeral_hidden_service({80: port}, key_type = key_type, key_content = key_content, await_publication = True)
            print("Resumed %s.onion" % service.service_id)







        return port

    def delete_private_key(self):
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')
        if os.path.exists(key_path):
            os.remove(key_path)
            print("Private key deleted")

    def start(self):
        """
        Start the server and listen for incoming connections.
        """
        # ask if user wants to create ephemeral or non-ephemeral hidden service
        print("Do you want to create an ephemeral or non-ephemeral hidden service?")
        print("1. Ephemeral")
        print("2. Non-ephemeral")
        print("3. Delete private key")
        choice = input("Enter choice: ")
        if choice == "1":
            port = self.ephemeral_onion()
        elif choice == "2":
            port = self.non_ephemeral_onion()
        elif choice == "3":
            self.delete_private_key()
            exit()
        self.__socket.bind(("127.0.0.1", port))

        self.__socket.listen(10)
        print('[Server] server is running......')


        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')


        while True:
            connection, address = self.__socket.accept()
            print('[Server] received a new connection', connection.getsockname(), connection.fileno())

            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()
