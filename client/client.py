import socket
import threading
import json
from cmd import Cmd
import socks


class Client(Cmd):
    """
    client
    """
    prompt = ''
    intro = '[Welcome] Simple chat room client (Cli version)\n' + '[Welcome] Type help to get help\n'

    def __init__(self):
        """
        structure
        """
        super().__init__()
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None
        self.__isLogin = False

    def __receive_message_thread(self):
        """
        accept message thread
        """
        while self.__isLogin:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                stripped = self.decode(buffer)
                if not stripped:
                    print('[Client] Unable to get data from server LINE 37')
                    self.__isLogin = False
                    break
                for i in stripped:
                    obj = json.loads(i)
                    print('[' + str(obj['sender_nickname']) + ']', obj['message'])
            except Exception as e:
                print('client line 38')
                print('[Client] Unable to get data from server', e)
                self.__isLogin = False
                break

    def decode(self, buffer):
        """
        decode buffer
        :param buffer: buffer
        :return: list
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
        return objects


    def __send_message_thread(self, message):
        """
        send message thread
        :param message: Message content
        """
        try:
            self.__socket.send(json.dumps({
                'type': 'broadcast',
                'sender_id': self.__id,
                'message': message
            }).encode())
        except Exception as e:
            print('client line 57')
            print(e)

    def start(self):
        """
        start the client
        """
        onion = input("Enter your onion address: ")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        server = (onion, 80)
        self.__socket.connect(server)
        # run cmdloop with the folling arguments
        self.cmdloop()

    def do_login(self, args):
        """
        login chat room
        :param args: parameter
        """
        nickname = args.split(' ')[0]

        # only login once
        if not self.__isLogin:
            # Send the nickname to the server to get the user id
            self.__socket.send(json.dumps({
                'type': 'login',
                'nickname': nickname
            }).encode())


            try:
                buffer = self.__socket.recv(1024).decode()
                print(buffer)
                obj = json.loads(buffer)
                if obj['id']:
                    # if id = -1 means the nickname is already in use
                    if obj['id'] == -1:
                        print('[Client] The nickname is already in use')
                        return
                    self.__nickname = nickname
                    self.__id = obj['id']
                    self.__isLogin = True
                    print('[Client] Successfully logged into the chat room')


                    thread = threading.Thread(target=self.__receive_message_thread)
                    thread.setDaemon(True)
                    thread.start()
            except Exception as e:
                print('client line 138')
                print(e)
                print("Server likely down")
                exit(0)
        else:
            print('[Client] You have already logged in')

    def do_s(self, args):
        """
        Send a message
        :param args: parameter
        """
        message = args
        # Show messages sent by yourself
        print('[' + str(self.__nickname) + ']', message)
        # Open child thread for sending data
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()

    def do_logout(self, args=None):
        """
        Sign out
        :param args: parameter
        """
        self.__socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id
        }).encode())
        self.__isLogin = False
        return True

    def do_help(self, arg):
        """
        help
        :param arg: parameter
        """
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login nickname - Login to the chat room, nickname is the nickname you choose')
            print('[Help] send message - Send a message, message is the message you entered')
            print('[Help] logout - exit chat room')
        elif command == 'login':
            print('[Help] login nickname - Login to the chat room, nickname is the nickname you choose')
        elif command == 'send':
            print('[Help] send message - Send a message, message is the message you entered')
        elif command == 'logout':
            print('[Help] logout - exit chat room')
        else:
            print('[Help] The command you want to know is not found')
