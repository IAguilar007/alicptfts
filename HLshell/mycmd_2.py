#!/usr/bin/env python

import sys
import os
sys.path.append(r'../alicptfts')
sys.path.append(r'./alicptfts')
#sys.path.append(r'../../alicpt_workspace/alicptfts')
#sys.path.append(r'../alicpt_workspace/alicptfts')
from alicptfts import AlicptFTS

from cmd import Cmd
from re import match
import sys, os
import socket
from io import StringIO
from functools import wraps

def toNum(x):
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except:
            return x

## Syntactic sugar fucntion
def parser(convertNum=True):
    def parser_base(func):
        @wraps(func)
        def wrapper(self,param):
            if (type(param)==str):
                params = list(filter(None,param.split(' ')))
            else:
                params = param

            if (convertNum):
                try:
                    params = tuple(map(toNum, params))
                except:
                    pass
            return func(self,*params)

        return wrapper
    return parser_base

class shell(Cmd):

    def __init__(self):
        ## Cmd
        Cmd.__init__(self)
        self.prompt = 'FTScmd> '
        self.intro = '####### Interactive Shell #######\nType help or ? to list commands.\n'


        ## socket
        self.hostIP = None
        self.port = self._DEFAULTPORT()  # Arbitrary non-privileged port
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.settimeout(60)

        ## fts
        self.fts = None
        self.scan_params = []


    @parser()
    def do_testType(self,*params):
        print('self ',self,params)
        for i in params:
            print(type(i))

    def _DEFAULTPORT(self):
        return 81

    def do_exit(self):
        '''exit the shell'''
        print("########### EXIT SHELL ###########")
        return True

    def help_exit(self):
        print('type q or qqq to leave')

    def default(self, inp):
        if inp == 'q' or bool(match(inp,'qqq+')):
            return self.do_exit()
        else:
            print("Command Not Found:", inp.split(' ')[0], file=sys.stderr)

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


    @parser()
    def do_FTSinit(self,*paramList):
        '''FTSinit IP username password'''
        if (not self.fts): self.fts = AlicptFTS()

        #paramList = list(filter(None,par.split(' ')))
        if (len(paramList)!=3):
            print('Require 3 parameters')
            print('FTSinit IP username password')
        else:
            self.fts.initialize(paramList[0],paramList[1],paramList[2])
            print('Status: Finish FTS initialization')

    @parser()
    def do_FTSconfig(self,*paramList):
        '''FTSconfig pos angle'''

        #paramList = list(filter(None, par.split(' ')))
        if (len(paramList) != 2):
            print('Require 2 parameters')
            print('FTSconfig pos angle ')
        else:
            self.fts.configure(paramList[0],paramList[1])

    def do_FTSstatus(self,par):
        '''Check the status of XPS'''
        self.fts.status()

    @parser()
    def do_FTSscan(self,*paramList):
        '''
        Params: 
            repeat -- number of times to repeat
            scan_range -- 
            TODO add parameters
        '''
        #paramList = list(filter(None, par.split(' ')))
        scan_range = (paramList[0], paramList[1])
        self.fts.scan(scan_range=scan_range)
        
    ## Remove unwant undoc commands
    do_EOF = do_exit
    self.__hidden = ('do_EOF','do_testType')

    def get_names(self):
        return [n for n in dir(self.__class__) if n not in self.__hidden]



class clientShell(shell):
    def __init__(self):
        super().__init__()
        self.intro = '####### Interactive Client Shell #######'
        self.prompt = 'cmd> '

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
            self.prompt = 'FTScmd> '


class serverShell(shell):
    def __init__(self):
        super().__init__()
        self.intro = '####### Interactive Server Shell #######'
        self.prompt = 'cmd> '


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
        self.prompt = 'FTScmd> '



if __name__ == '__main__':
    # header
    # modes = ['Server','Client']
    print("Choose Server or Client Mode")
    print("Press 1 to Server and 2 to Client")
    print("Press ENTER to run locally")

    while True:
        mode = input("Mode: ")
        #mode = '1'
        if (mode.isspace() or not mode):
            mode = '0'
            break
        elif (mode.isdecimal()):
            if (int(mode)>=0 or int(mode)<=2):
                #print(f'Open {modes[int(mode)-1]} Shell')
                break
        elif mode == 'q' or bool(match(mode, 'qqq+')):
            exit()

    if (int(mode)==1): serverShell().cmdloop()
    elif (int(mode)==2): clientShell().cmdloop()
    else: shell().cmdloop()
    #shell().cmdloop()
#HLcmd().cmdloop()

