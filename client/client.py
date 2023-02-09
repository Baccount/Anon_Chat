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
                obj = json.loads(buffer)
                print('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']', obj['message'])
            except Exception:
                print('[Client] Unable to get data from server')

    def __send_message_thread(self, message):
        """
        send message thread
        :param message: Message content
        """
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        """
        start the client
        """
        onion = input("Enter your onion address: ")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        server = (onion, 80)
        self.__socket.connect(server)
        self.cmdloop()

    def do_login(self, args):
        """
        login chat room
        :param args: parameter
        """
        nickname = args.split(' ')[0]

        # Send the nickname to the server to get the user id
        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())


        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.__isLogin = True
                print('[Client] Successfully logged into the chat room')


                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Client] Cant log in to the chat room')
        except Exception:
            print('[Client] Unable to get data from server')

    def do_send(self, args):
        """
        Send a message
        :param args: parameter
        """
        message = args
        # Show messages sent by yourself
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']', message)
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
