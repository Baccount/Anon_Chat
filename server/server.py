import socket
import threading
import json
from stem.control import Controller
from random import randint


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

    def __user_thread(self, user_id):
        """
        user thread
        :param user_id: user id
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] user', user_id, nickname, 'join the chat room')
        # self.__broadcast(message='user ' + str(nickname) + 'joined the chat room')


        try:
            while True:
                buffer = b''
                chunk = connection.recv(1024)
                print(f"chunk: {chunk}")
                if chunk:
                    buffer += chunk
                else:
                    break
                # Decode the buffer into a string
                buffer = buffer.decode()
                print(f"buffer: {buffer}")
                # Split the buffer into individual JSON objects
                                # Split the buffer into individual JSON objects
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
                    for obj in objects:
                        if obj:
                            # Parse the JSON object
                            obj = json.loads(obj)
                                    # Broadcast message
                            if obj['type'] == 'broadcast':
                                self.__broadcast(obj['sender_id'], obj['message'])
                            elif obj['type'] == 'logout':
                                print('[Server] user', user_id, nickname, 'exit chat room')
                                self.__broadcast(message='user ' + str(nickname) + '(' + str(user_id) + ')' + 'exit chat room')
                                self.__connections[user_id].close()
                                self.__connections[user_id] = None
                                self.__nicknames[user_id] = None
                                break
                            else:
                                print('[Server] user', user_id, nickname, 'exit chat room')
                                print('server line 51')
                                self.__connections[user_id].close()
                                # remove the user from the list
                                self.__connections[user_id] = None
                                self.__nicknames[user_id] = None
                                # remove the user from the list
                            break
        except Exception as e:
            print('[Server] user', user_id, nickname, 'exit chat room')
            print('server line 60')
            print(e)
            self.__connections[user_id].close()
            # remove the user from the list
            self.__connections[user_id] = None
            self.__nicknames[user_id] = None
            # remove the user from the list

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
        # try to accept data
        # noinspection PyBroadException
        try:
            while True:
                buffer = connection.recv(1024).decode()
                print(buffer)
                # parsed into json data
                obj = json.loads(buffer)
                # If it is a connection command, then return a new user number to receive the user connection
                #  and obj['nickname'] not in self.__nicknames
                if obj['type'] == 'login':
                    # check if the nickname is already in use
                    if obj['nickname'] in self.__nicknames:
                        connection.send(json.dumps({
                            'id': -1
                        }).encode())
                        continue
                    self.__connections.append(connection)
                    self.__nicknames.append(obj['nickname'])
                    connection.send(json.dumps({
                        'id': len(self.__connections) - 1
                    }).encode())
                    # start a new thread
                    thread = threading.Thread(target=self.__user_thread, args=(len(self.__connections) - 1,))
                    thread.setDaemon(True)
                    thread.start()
                    break

        except Exception as e:
            print('server line 95')
            print(e)
            print('[Server] Unable to accept data:', connection.getsockname(), connection.fileno())




    def create_onion(self):
        '''
        create ephemeral hidden services
        '''
        port = randint(10000, 65535)
        controller = Controller.from_port(port = 9051)
        controller.authenticate()

        response = controller.create_ephemeral_hidden_service({80: port}, await_publication = True)
        print(f"Created new hidden service with onion address: {response.service_id}.onion")
        return port

    def start(self):
        """
        start server
        """
        port = self.create_onion()

        # bind port
        self.__socket.bind(("127.0.0.1", port))
        # 启用监听
        self.__socket.listen(10)
        print('[Server] server is running......')

        # enable listening
        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')

        # start listening
        while True:
            connection, address = self.__socket.accept()
            print('[Server] received a new connection', connection.getsockname(), connection.fileno())

            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()
