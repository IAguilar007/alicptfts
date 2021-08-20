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

class shell(Cmd):

    def __init__(self):
        ## Cmd
        Cmd.__init__(self)
        self.prompt = 'FTScmd> '
        self.intro = '####### Interactive Shell #######'

        ## socket
        self.hostIP = None
        self.port = self._DEFAULTPORT()  # Arbitrary non-privileged port
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.settimeout(60)

        ## fts
        self.fts = None
        self.scan_params = []

    def _DEFAULTPORT(self):
        return 81

    def do_exit(self, par):
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

    def do_FTSsettings(self, par):
        '''FTSsettings stagename velocity acceleration  
        
        Stagename can be PL (pointing linear), PR (pointing rotary), or ML (moving linear)
        Velocity must be between 1 and 200 (1 and 20 for PR)
        Acceleration must be between 1 and 600 (1 and 80 for PR)
        PR and PL are moved with FTSconfig, and ML is moved with FTSscan
        '''

        if(self.fts is None):
            print('FTS not yet initialized!')
            return 
        paramList = list(filter(None,par.split(' ')))
        if (len(paramList)!=3):
            print('Require 3 parameters')
            print('FTSsettings stagename velocity acceleration')
            return 

        MAX_VEL = 200
        MAX_ACC = 600

        min_val = 1
        if(paramList[0] == 'PL'):
            stagename = 'PointingLinear'
            
        elif(paramList[0] == 'PR'):
            MAX_VEL = 20
            MAX_ACC = 80
            stagename = 'PointingRotary' 
        
        elif(paramList[0] == 'ML'):
            stagename = 'MovingLinear'
        
        else:
            print('Requires stagename to be either PL, PR, or ML ' +
                '(pointing linear, pointing rotary, or moving linear)')
            return 

        try:
            velocity = float(paramList[1])
            acceleration = float(paramList[2])
        except ValueError:
            print('Velocity and acceleration must be floats')

        if (velocity < min_val or velocity > MAX_VEL):
            print('Velocity not in allowed range')
            return 

        if (acceleration < min_val or acceleration > MAX_ACC):
            print('Acceleration not in allowed range')
            return 


        self.fts.set_motion_params(stagename, [velocity, acceleration])

    def do_FTSinit(self,par):
        '''FTSinit IP username password
        This is required to initialize the NewportXPS machine before anything else is run.
        '''
        if (not self.fts): self.fts = AlicptFTS()

        paramList = list(filter(None,par.split(' ')))
        if (len(paramList)!=3):
            print('Require 3 parameters')
            print('FTSinit IP username password')
        else:
            self.fts.initialize(paramList[0],paramList[1],paramList[2])
            print('Status: Finish FTS initialization')

    def do_FTSconfig(self,par):
        '''FTSconfig pos angle
        Position is between 0 and 500. Moves the PL (pointing linear) to desired location.
        Angle is in degrees. No range limit. Rotates the PR (pointing rotary) to desired angle.
        '''
        if(self.fts is None):
            print('FTS not yet initialized!')
            return 
        paramList = list(filter(None, par.split(' ')))
        if (len(paramList) != 2):
            print('Require 2 parameters')
            print('FTSconfig pos angle ')
            return 
        try:
            pos = float(paramList[0])
        except ValueError:
            print('Position must be a float')
            return 
        if(pos < min_pos or pos > max_pos):
            print('Position not within range')
            return 
        
        try:
            angle = float(paramList[1])
        except ValueError:
            print('Angle must be a float')

        self.fts.configure(pos, angle)

    def do_FTSstatus(self,par):
        '''Check the status of XPS'''
        if(self.fts is None):
            print('FTS not yet initialized!')
            return 
        self.fts.status()

    def do_FTSscan(self,par):
        '''FTSscan n_repeat scan_range_min scan_range_max
        n_repeat is number of times to repeat the scan
        scan_range_min and _max must be between 0 and 500
        Scanning velocity can be changed in FTSsettings, where the stagename is ML (moving linear)
        '''
        if(self.fts is None):
            print('FTS not yet initialized!')
            return 
        paramList = list(filter(None, par.split(' ')))
        if (len(paramList)!=3 and len(paramList)!=4):
            print('Require 3 or 4parameters')
            print('FTSscan n_repeat scan_range_min scan_range_max filename(optional)')
            return

        min_scan = 0
        max_scan = 500
        try:
            scan_range = (float(paramList[1]), float(paramList[2]))
        except ValueError:
            print('Scan range must be input as floats')
            return 
        if(scan_range[0] > scan_range[1]):
            print('Min scan range must be smaller than max scan range')
            return 
        elif(scan_range[0] < min_scan or scan_range[1] > max_scan):
            print('Scan range not within range')
            return 
        try:
            n_repeat = int(paramList[0])
        except ValueError:
            print('n_repeat must be an integer')
            return 

        filename = None
        if(len(paramList) == 4):
            filename = paramList[3]
        self.fts.scan(repeat=n_repeat, scan_range=scan_range, filename=filename)
        




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

    if (int(mode)==1): serverShell().cmdloop()
    elif (int(mode)==2): clientShell().cmdloop()
    else: shell().cmdloop()
    #shell().cmdloop()
#HLcmd().cmdloop()

