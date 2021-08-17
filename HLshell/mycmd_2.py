from cmd import Cmd
from re import match
import sys, os
import socket
from io import StringIO

class shell(Cmd):

    def __init__(self):
        ## Cmd
        Cmd.__init__(self)
        self.prompt = 'FTScmd> '
        self.intro = '####### Interactive Shell #######'

        ## socket
        self.hostIP = ''
        self.port = self._DEFAULTPORT()  # Arbitrary non-privileged port
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.settimeout(60)

    def _DEFAULTPORT(self):
        return 81

    def do_exit(self):
        '''exit the shell'''
        print("EXIT")
        return True

    def help_exit(self):
        print('type q or qqq to leave')

    def default(self, inp):
        if inp == 'q' or bool(match(inp,'qqq+')):
            return self.do_exit()

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
        if (out): print(out, end='')
        if (err): print(err, file=sys.stderr, end='')
        return out, err

    do_EOF = do_exit
    help_EOF = help_exit

class clientShell(shell):
    def __init__(self):
        super().__init__()
        self.intro = '####### Interactive Client Shell #######'


    def preloop(self):
        pass
        #print('Open Client Shell')

    def do_connect(self,par):
        '''connect IP [port=80]'''
        paramList = list(filter(None,par.split(' ')))
        if (len(paramList) > 2 or len(paramList)==0):
            print('Require 1 or 2 parameters')
        else:
            self.hostIP = paramList[0]
            if (len(paramList)==2 and paramList[1].isdecimal()):
                self.port = paramList[1]
            else:
                self.port = self._DEFAULTPORT()
                if (len(paramList)==2): print('Second parameters (port) should be a number.\nUse default setting, port ', self._DEFAULTPORT())
            try:
                self.socket.connect((self.hostIP,self.port))
            except socket.error as msg:
                print(msg)

            self.socket.send(socket.gethostname().encode())
            cwd = self.socket.recv(1024)
            print("STATUS: connect to machine: ", cwd.decode())


class serverShell(shell):
    def __init__(self):
        super().__init__()
        self.intro = '####### Interactive Server Shell #######'


    def preloop(self):
        pass
        #print('Open Server Shell')

    def do_connect(self,par):
        '''connect [port=80]'''
        #print('Type the port used to connect. Press ENTER to use default setting')
        if (par.isdecimal()):
            print('Connect by port ', int(par))
            self.port = int(par)
        else:  # default setting, port = 80
            self.port = self._DEFAULTPORT()
            print('Use default setting: port ', self.port)

        try:
            aa = '127.0.0.1'
            self.socket.bind(('', self.port))
            self.socket.listen(5)

        except socket.error as e:
            print("Fail to bind", e)
            return -1

        # recieve message from client
        client_socket, client_address = self.socket.accept()
        print(f"Bind to {client_address[0]}:{client_address[1]}")

        # if connect
        cwd = client_socket.recv(1024).decode()
        print("STATUS: connect to machine: ", cwd)
        client_socket.send(socket.gethostname().encode())


if __name__ == '__main__':
    # header
    modes = ['Server','Client']
    print("Choose Server or Client Mode")
    print("Press 1 for Server and 2 for Client")
    while True:
        #mode = input("Mode: ")
        mode = '1'
        if (mode.isdecimal()):
            if (int(mode)==1 or int(mode)==2):
                #print(f'Open {modes[int(mode)-1]} Shell')
                break

    if (int(mode)==1): serverShell().cmdloop()
    else: clientShell().cmdloop()

    #shell().cmdloop()
#HLcmd().cmdloop()

