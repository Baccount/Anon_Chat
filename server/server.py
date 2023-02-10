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

    def __user_thread(self, user_id):
        """
        user thread
        :param user_id: user id
        """
        connection = self.__connections[user_id]
        nickname = self.__nicknames[user_id]
        print('[Server] user', user_id, nickname, 'join the chat room')
        self.__broadcast(message='user ' + str(nickname) + '(' + str(user_id) + ')' + 'join the chat room')

        # 侦听
        while True:
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # parsed into json data
                obj = json.loads(buffer)
                # If it is a broadcast command
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
                    print('[Server] Unable to parse json packet:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] connection failure:', connection.getsockname(), connection.fileno())
                self.__connections[user_id].close()
                self.__connections[user_id] = None
                self.__nicknames[user_id] = None

    def __broadcast(self, user_id=0, message=''):
        """
        broadcast
        :param user_id: user id (0 is the system)
        :param message: broadcast content
        """
        for i in range(1, len(self.__connections)):
            if user_id != i and self.__connections[i]:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message
                }).encode())

    def __waitForLogin(self, connection):
        # try to accept data
        # noinspection PyBroadException
        try:
            while True:
                buffer = connection.recv(1024).decode()
                # parsed into json data
                obj = json.loads(buffer)
                # If it is a connection command, then return a new user number to receive the user connection
                if obj['type'] == 'login':
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
                else:
                    print('[Server] Unable to parse json packet:', connection.getsockname(), connection.fileno())
        except Exception:
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
