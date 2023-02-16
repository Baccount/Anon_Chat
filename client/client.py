import threading
import json
from cmd import Cmd
from connect_tor import Tor


class Client(Cmd):
    """
    client
    """
    prompt = ''
    intro = 'Welcom to AnonChat \n'

    def __init__(self):
        """
        structure
        """
        super().__init__()
        # create a new tor instance
        self.tor = Tor()
        self.__id = None
        self.__nickname = None
        self.__isLogin = False

    def __receive_message_thread(self):
        """
        Continuously receive messages from the server.
        """
        while self.__isLogin:
            try:
                buffer = self.tor.socket.recv(1024).decode()
                stripped = self.decode(buffer)
                if not stripped:
                    print('[Client] Server offline, exiting LINE 37')
                    exit()
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
        Decode the buffer into individual JSON objects.

        :param buffer: The buffer to be decoded.
        :return: A list of JSON objects.
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
        Send a message to the server.

        :param message: The message to be sent.
        """
        try:
            self.tor.socket.send(json.dumps({
                'type': 'broadcast',
                'sender_id': self.__id,
                'message': message
            }).encode())
        except BrokenPipeError as e:
            print(f'{e} client line 86')
            exit(0)
        except Exception as e:
            print('client line 87')
            print(e)

    def start(self):
        """
        Connect to the server using the onion address.
        """
        onion = input("Enter your onion address: ")
        # start tor onion service
        self.tor.start_onion(onion)
        self.cmdloop()

    def do_login(self, args):
        """
        Login to the chat room.

        :param args: The nickname to be used for the login.
        """
        nickname = args.split(' ')[0]

        # only login once
        if not self.__isLogin:
            # Send the nickname to the server to get the user id
            self.tor.socket.send(json.dumps({
                'type': 'login',
                'nickname': nickname
            }).encode())


            try:
                buffer = self.tor.socket.recv(1024).decode()
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
        Send a message to the chat room.

        :param args: The message to be sent.
        """
        # only send message after login
        if self.__isLogin:
            message = args
            # Show messages sent by yourself
            print('[' + str(self.__nickname) + ']', message)
            # Open child thread for sending data
            thread = threading.Thread(target=self.__send_message_thread, args=(message,))
            thread.setDaemon(True)
            thread.start()
        else:
            print('[Client] You have not logged in yet')

    def do_logout(self, args=None):
        """
        Logout from the chat room.
        """
        self.tor.socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id
        }).encode())
        self.__isLogin = False
        return True

    def do_help(self, arg):
        """
        Display help information for the given command.
        :param arg: the command for which help information is needed
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
