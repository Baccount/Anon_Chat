from json import dumps, loads
from threading import Thread
from cmd import Cmd

from logging_msg import log_msg
from scrips.scripts import decode, g, r

from .connect_tor import ConnectTor


class Client(Cmd):
    """
    client
    """

    prompt = ""
    intro = "Welcom to AnonChat \n"

    def __init__(self):
        """
        structure
        """
        super().__init__()
        # create a new tor instance
        self.tor = ConnectTor()
        self.__id = None
        self.__nickname = None
        self.__isLogin = False
        self.onion_address = None

    def __receive_message_thread(self):
        """
        Continuously receive messages from the server.
        """
        while self.__isLogin:
            try:
                buffer = self.tor.socket.recv(1024).decode()
                decoded = decode(buffer)
                if not decoded or decoded == "":
                    # We lost connection restart the client
                    log_msg("__receive_message_thread", "Message not decoded", buffer)
                    self.tor.socket.close()
                    self.start()

                for i in decoded:
                    obj = loads(i)
                    print("[" + str(obj["sender_nickname"]) + "]", obj["message"])
            except Exception as e:
                log_msg("__receive_message_thread", "Exception ", e)
                self.__isLogin = False
                break

    def __send_message_thread(self, message):
        """
        Send a message to the server.

        :param message: The message to be sent.
        """
        try:
            self.tor.socket.send(
                dumps(
                    {"type": "broadcast", "sender_id": self.__id, "message": message}
                ).encode()
            )
        except BrokenPipeError as e:
            log_msg("__send_message_thread", "BrokenPipeError", e)
            exit(0)
        except Exception as e:
            log_msg("__send_message_thread", "Exception ", e)
            print(e)

    def start(self):
        """
        Connect to the server using the onion address.
        """
        onion = input("Enter your onion address: ")
        if onion == "quit" or onion == "exit" or onion == "q":
            exit(0)
        self.onion_address = onion
        # start tor onion service
        if not self.tor.connect_onion(onion):
            # Onion service not found, ask user to try again
            print(r("Onion service not found, please try again"))
            self.start()
        self.cmdloop()

    def do_login(self, args):
        """
        Login to the chat room.

        :param args: The nickname to be used for the login.
        """
        nickname = args.split(" ")[0]

        # only login once
        if not self.__isLogin:
            # Send the nickname to the server to get the user id
            self.tor.socket.send(
                dumps({"type": "login", "nickname": nickname}).encode()
            )

            try:
                buffer = self.tor.socket.recv(1024).decode()
                log_msg("Client", "do_login", f"buffer{buffer}")
                obj = loads(buffer)
                if obj["id"]:
                    
                    # if id = -1 means the nickname is already in use
                    if obj["id"] == -1:
                        print("[Client] The nickname is already in use")
                        log_msg("do_login", "The nickname is already in use")
                        return
                    
                    # if id = -2 means the nickname is disallowed/banned
                    if obj["id"] == -2:
                        print("[Client] The nickname is disallowed/banned")
                        log_msg("do_login", "The nickname is disallowed/banned")
                        return
                    self.__nickname = nickname
                    self.__id = obj["id"]
                    self.__isLogin = True
                    print("Successfully logged into the chat room")
                    log_msg("Client", "do_login", "Successfully logged into the chat room")

                    thread = Thread(target=self.__receive_message_thread)
                    thread.setDaemon(True)
                    thread.start()
            except Exception as e:
                print("Server likely down")
                log_msg("do_login", "Exception ", e)
                exit(0)
        else:
            print("[Client] You have already logged in")
            log_msg("do_login", "You have already logged in")

    def do_s(self, args):
        """
        Send a message to the chat room.

        :param args: The message to be sent.
        """
        # only send message after login
        if self.__isLogin:
            message = args
            # Show messages sent by yourself
            print("[" + str(self.__nickname) + "]", message)
            # Open child thread for sending data
            thread = Thread(
                target=self.__send_message_thread, args=(message,)
            )
            thread.setDaemon(True)
            thread.start()
        else:
            print("[Client] You have not logged in yet")
            log_msg("do_s", "You have not logged in yet")

    def do_logout(self, args=None):
        """
        Logout from the chat room.
        """
        self.tor.socket.send(
            dumps({"type": "logout", "sender_id": self.__id}).encode()
        )
        self.__isLogin = False
        log_msg("do_logout", "You have logged out")
        return True

    def do_h(self, args=None):
        """
        Show help menu.
        """
        print("login <nickname> - login to the chat room")
        print("s - send message from server to all clients")
        print("o - show onion address")
        print("logout - logout from the chat room")
        print("h - show help menu")
        print("q - quit the chat room")

    def do_o(self, args):
        # print the onion address
        onion = g(self.onion_address)
        print(f"{onion}")

    def do_quit(self, args=None):
        """
        Quit the chat room.
        """
        self.do_logout()
        exit(0)
        # exit without calling force kill tor for now
        # force_kill_tor()