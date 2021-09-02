#!/usr/bin/env python
import sys, os
import pickle
import time
sys.path.append(r'../alicptfts')
sys.path.append(r'./alicptfts')


from cmd import Cmd
from re import match
import socket
from io import StringIO
from functools import wraps
import argparse

import msvcrt
import threading

from alicptfts import AlicptFTS


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


def print_err(*err, wrapper='*****',sep=' ', end='\n', file=sys.stderr, flush=False):
    print(str(wrapper) + ' ', file=file,end='')
    print(*err, file=file,end='',sep=sep)
    print(' ' + str(wrapper), file=file, flush=flush,end=end)


class shell(Cmd):
    DEFAULT_TIMEOUT = 5
    BUFFER_SIZE = 1024 * 128
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
        self.socket.settimeout(shell.DEFAULT_TIMEOUT)

        ## fts
        self.fts = None
        self.scan_params = []
        self.doRemote = False

    def _checkInit(func):
        @wraps(func)
        def wrapper(self, *params, **kargs):
            try:
                if (self.fts is None):
                    print_err('FTS is not yet initialized!')
                    print_err('Did you mean to send the command instead?')
                    return #lambda *params, **kargs: None
                else:  ## Connect
                    return func(self,*params,**kargs)
            except Exception as e:
                ''' len(params)==0 '''
                ## Try not to kill the loop if possible
                print_err('Error:',e)

        return wrapper

    @parser()
    def do_testType(self,*params):
        print('self ',self,params)
        for i in params:
            print(type(i))

    # do nothing if command is empty
    def emptyline(self):
        pass 

    ## use for test
    def do_print(self,par):
        '''print any argument you want'''
        print('"print" command is used for test\narg: ',par)

    def _DEFAULTPORT(self):
        return 81

    def do_exit(self, par):
        '''exit the shell'''
        print("########### EXIT SHELL ###########")
        return True

    def help_exit(self):
        print('type exit or q to leave')

    def default(self, inp):
        if inp == 'q' or bool(match(inp,'qqq+')):
            return self.do_exit(inp)
        else:
            print_err("Command Not Found:", inp.split(' ')[0])

    def run_cmdbase(self,func,line):
        re = self.onecmd(line)
        print(re, 'nothing')

    def run_command(self,func, line):
        temp_out = StringIO()
        temp_err = StringIO()
        sys.stdout = temp_out
        sys.stderr = temp_err

        try:
            func(line)
        except:
            print_err('Error: ' + func.__name__ + '('+line+')')
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        out = temp_out.getvalue()
        err = temp_err.getvalue()
        if (out): print(out, end='')
        if (err): print_err(err)
        return out, err

    @parser()
    @_checkInit
    def do_FTSsettings(self,*paramList):
        '''Command: FTSsettings stagename velocity acceleration  
        
        Stagename can be PL (pointing linear), PR (pointing rotary), or ML (moving linear)
        Velocity must be between 1 and 200 (1 and 20 for PR)
        Acceleration must be between 1 and 600 (1 and 80 for PR)
        PR and PL are moved with FTSconfig, and ML is moved with FTSscan
        '''

        if (len(paramList)!=3):
            print_err('Require 3 parameters')
            print_err('FTSsettings stagename velocity acceleration')
            return

        MAX_VEL = AlicptFTS.MAX_VEL
        MAX_ACC = AlicptFTS.MAX_ACCEL

        min_accel = AlicptFTS.MIN_ACCEL
        min_vel = AlicptFTS.MIN_VEL

        if(paramList[0] == 'PL'):
            stagename = 'PointingLinear'
            
        elif(paramList[0] == 'PR'):
            MAX_VEL = AlicptFTS.MAX_R_VEL
            MAX_ACC = AlicptFTS.MAX_R_ACCEL
            stagename = 'PointingRotary' 
        
        elif(paramList[0] == 'ML'):
            stagename = 'MovingLinear'
        
        else:
            print_err('Requires stagename to be either PL, PR, or ML ' +
                '(pointing linear, pointing rotary, or moving linear)')
            return

        try:
            velocity = float(paramList[1])
            acceleration = float(paramList[2])
        except ValueError:
            print_err('Velocity and acceleration must be float')
            return

        if (velocity < min_vel or velocity > MAX_VEL):
            print_err('Velocity is not in allowed range')
            return

        if (acceleration < min_accel or acceleration > MAX_ACC):
            print_err('Acceleration is not in allowed range')
            return

        self.fts.set_motion_params(stagename, [velocity, acceleration])

    @parser()
    def do_FTSinit(self,*paramList):
        '''Command: FTSinit IP username password

        This is required to initialize the NewportXPS machine before anything else is run.
        '''

        

        if (len(paramList)!=3):
            print_err('Require 3 parameters')
            print_err('FTSinit IP username password')
            return

        if (not self.fts): self.fts = AlicptFTS()
        try:
            self.fts.initialize(paramList[0],paramList[1],paramList[2])
            print('Status: Finish FTS initialization')

        except TypeError:
            print_err('FTSinit IP(str) username(str) password(str)')
            return

        except:
            print_err('Connection failed')
            print_err('Did you mean to send the command instead?')
            return




    @parser()
    @_checkInit
    def do_FTSconfig(self,*paramList):
        '''Command: FTSconfig pos angle

        Position is between 0 and 500. Moves the PL (pointing linear) to desired location.
        Angle is in degrees. No range limit. Rotates the PR (pointing rotary) to desired angle.
        '''
        if (len(paramList) != 2):
            print_err('Require 2 parameters')
            print_err('FTSconfig pos angle ')
            return

        min_pos = AlicptFTS.MIN_POS
        max_pos = AlicptFTS.MAX_POS
        try:
            pos = float(paramList[0])
        except ValueError:
            print_err('Position must be a float')
            return
        if(pos < min_pos or pos > max_pos):
            print_err('Position is not in tne range')
            return
        
        try:
            angle = float(paramList[1])
        except ValueError as e:
            print_err('Angle must be a float')
            return

        self.fts.configure(pos, angle)

    @_checkInit
    def do_FTSstatus(self,par):
        '''Check the status of XPS'''
        self.fts.status()

    @parser()
    @_checkInit
    def do_FTSscan(self,*paramList):
        '''Command: FTSscan n_repeat scan_range_min scan_range_max filename(optional)

        n_repeat is number of times to repeat the scan
        scan_range_min and _max must be between 0 and 500 (mm)
        Scanning velocity can be changed in FTSsettings, where the stagename is ML (moving linear)
        If the filename is specified, the scanning saves the stage positions into the file. Otherwise, the
            information is saved in scan_range_[min]_[max]__configure_[pos]_[angle].dat
        '''

        if (len(paramList)<3 or len(paramList)>4):
            print_err('Require 3 or 4 parameters')
            print_err('FTSscan n_repeat scan_range_min scan_range_max filename(optional)')
            return

        min_scan = AlicptFTS.MIN_POS
        max_scan = AlicptFTS.MAX_POS
        try:
            scan_range = (float(paramList[1]), float(paramList[2]))
        except ValueError:
            print_err('Scan range must be input as floats')
            return

        if(scan_range[0] > scan_range[1]):
            scan_range[0], scan_range[1] = scan_range[1], scan_range[0]
            #print('*****Min scan range must be smaller than max scan range')


        if(scan_range[0] < min_scan or scan_range[1] > max_scan):
            print_err('Scan range not within range')
            return

        try:
            n_repeat = int(paramList[0])
        except ValueError:
            print_err('n_repeat must be an integer')
            return

        filename = None
        if(len(paramList) == 4):
            filename = paramList[3]
        self.fts.scan(repeat=n_repeat, scan_range=scan_range, filename=filename)

    ## Remove unwant undoc commands
    do_EOF = do_exit
    __hidden = ('do_EOF','do_testType')

    def get_names(self): ## Don't change the name
        return [n for n in dir(self.__class__) if n not in self.__hidden]


## Laptop
class clientShell(shell):
    DEFAULT_TIMEOUT = 6
    def __init__(self, ip):
        super().__init__()
        self.intro = '####### Interactive Client Shell #######'
        self.prompt = 'cmd> '
        self.doRemote = True
        self.server_ip = ip
        self.is_connected = False 
        self.is_connecting = False
        self.waiting_for_cmd = False
        self.debug_mode = False

    def preloop(self):
        '''Automatically connects and waits for commands'''
       
        self.do_start('')

       
    
    @parser()
    def do_start(self, *par):
        '''start [IP] 
        
        Start automatically connecting and receiving commands from server'''
        self.debug_mode = False
        if(len(par) > 0):
            self.server_ip = par

        # I probably should've switched preloop and start
        pressed_key = '_'
        EXIT = 'q'
        self.is_connecting = False

        while(not self.debug_mode):
            connect_thread = threading.Thread(target=self.do_connect, args=[self.server_ip])
        
            if(msvcrt.kbhit()):
                pressed_key = msvcrt.getwch()
            if(pressed_key == EXIT):
                self.debug_mode = True
                break
            # If connected, then wait for commands
            if(self.is_connected):
                self.do_wait(1)
            else:
                # Continuously try to connect until is connected
                # Do not start another thread if current thread is still running
                # for some reason thread.is_alive() doesn't work here
                if(not self.is_connecting and not self.is_connected):
                    self.is_connecting = True
                    connect_thread.start()
        print('Debug mode. Type "start" to continue receiving commands from server.')

    @parser()
    def do_connect(self,*paramList):
        '''connect IP [port=81]'''

        if (len(paramList) > 2 or len(paramList)==0):
            print_err('Require 1 or 2 parameters')
            self.is_connecting = False
            return

        self.hostIP = paramList[0]
        if (len(paramList)==2 and paramList[1]>0):
            self.port = paramList[1]
        else:
            self.port = self._DEFAULTPORT()
            if (len(paramList)==2): 
                print_err('Second parameters (port) should be a number.\nUse default setting, port ', self._DEFAULTPORT())
        
        connect_timeout = clientShell.DEFAULT_TIMEOUT
        self.socket = socket.socket()
        self.socket.settimeout(connect_timeout)
        print('Attempting to connect to ' + str(self.hostIP) + ':' + str(self.port))
        try:
            self.socket.connect((self.hostIP,self.port))
        except socket.error as msg:
            print_err('Server is not receiving connections')
            self.is_connecting = False
            return 
        except TypeError:
            print_err('Please enter a proper IP')
            self.is_connecting = False
            return 
        except socket.timeout:
            print_err('Connection timed out after ' + str(connect_timeout) + ' seconds')
            self.is_connecting = False
            return 

        self.socket.settimeout(shell.DEFAULT_TIMEOUT)
        self.socket.sendall(socket.gethostname().encode())
        
        try:
            cwd = self.socket.recv(1024)
            print("STATUS: connect to machine: ", cwd.decode())
            self.prompt = 'FTScmd> '
            self.is_connected = True
        except (ConnectionAbortedError,ConnectionResetError) as e :
            print_err('Connection not ready, try again')
            self.is_connecting = False
            return 
        except socket.timeout:
            print_err('Connection timed out after ' + str(connect_timeout) + ' seconds')
            self.is_connecting = False
            return 
        self.is_connecting = False

    def receive_command(self, timeout, EXIT='q'):
        '''
        Waits for a command from the server every [timeout] seconds
        If connection is lost in the middle of receiving a command,
        then we exit the loop
        '''
        try:
            self.socket.settimeout(timeout)
            while(self.waiting_for_cmd):
                try:
                    command = self.socket.recv(shell.BUFFER_SIZE).decode()
                except socket.timeout:
                    continue 
                print('Command received: ' + str(command))
                cmd_received = pickle.dumps(['Command Received', None])
                self.socket.send(cmd_received)

                out,err = self.run_command(self.onecmd,command)
                codeOut = pickle.dumps([out,err])  ## encode the output list
                self.socket.send(codeOut)
                print('Command completed')
                print('Press ' + str(EXIT) +  ' to exit loop')
                print('Waiting for the command...')
        except (ConnectionAbortedError, ConnectionResetError):
            print_err('Connection lost. Please reconnect.')
            self.waiting_for_cmd = False
            self.is_connected = False
            return 

    def do_wait(self,par):
        '''wait [refresh_time]'''
        self.debug_mode = False
        EXIT = 'q'
        refresh = 1
        try:
            refresh = float(par)
        except ValueError:
            print_err('Refresh rate must be a float, using default refresh time')
            

        pressed_key = ''
        self.waiting_for_cmd = True 
        wait_thread = threading.Thread(target=self.receive_command, args=[refresh, EXIT])
        
        print('Press ' + str(EXIT) +  ' to stop receiving commands and enter debug mode')
        print('Waiting for command from server...')
        
        while (self.waiting_for_cmd):
            
            # waits for a command in the background
            if(not wait_thread.is_alive()):
                wait_thread.start()

            # if we EXIT, then stop waiting for commands
            if(msvcrt.kbhit()):
                pressed_key = msvcrt.getwch()
            if(pressed_key == EXIT):
                self.waiting_for_cmd = False
                self.debug_mode = True
 
        print('Done receiving commands')

            

## GCS
class serverShell(shell):
    def __init__(self):
        super().__init__()
        self.intro = '####### Interactive Server Shell #######'
        self.prompt = 'cmd> '
        self.doRemote = True
        self.clientSocket = None
        

    def preloop(self):
        pass
        #print('Open Server Shell')

    @parser()
    def do_connect(self,*par):
        '''connect [port=81 timeout=30 seconds]'''
        #print('Type the port used to connect. Press ENTER to use default setting')
        if(len(par)>0):
            try:
                self.port = int(par[0])
                print('Connect by port ', self.port)
            except Exception as e:  # default setting, port = 81
                self.port = self._DEFAULTPORT()
                print_err(e)
                print_err('Using default setting: port ', self.port)
        if(len(par) == 2):
            try:
                timeout = float(par[1])
            except:
                timeout = shell.DEFAULT_TIMEOUT
        else:
            timeout = shell.DEFAULT_TIMEOUT
        print('Will wait for connection request for ' + str(timeout) + ' seconds') 

        try:
            #ip = '127.0.0.1'
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(timeout)
            self.socket.bind(('', self.port))
            self.socket.listen(5)

        except socket.error as e:
            print_err("Fail to bind" + str(e))
            return 
        
        # recieve message from client
        try:
            self.clientSocket, client_address = self.socket.accept()
        except socket.timeout:
            print_err('Connection timed out after ' + str(timeout) + ' seconds.')
            return 
        print(f"Bind to {client_address[0]}:{client_address[1]}")

        # if connect
        cwd = self.clientSocket.recv(1024).decode()
        print("STATUS: connect to machine: ", cwd)
        self.clientSocket.send(socket.gethostname().encode())
        self.prompt = 'FTScmd> '


    def do_send(self,par):
        '''send [any other command to the server]'''
        if(len(par) < 1):
            print_err("No command sent")
            return 
        print('Sending params: ' + str(par))
        self.clientSocket.settimeout(clientShell.DEFAULT_TIMEOUT)
        try:
            try:
                self.clientSocket.send(par.encode())
        
            except socket.timeout:
                print_err('Connection timed out. Is the client connected?')
                return 
            print('Command sent to client')
            try:
                print('Client is receiving Command')
                cmd_received = self.clientSocket.recv(shell.BUFFER_SIZE)
            except socket.timeout:
                print_err('Connection timed out')
                print_err('Is the client receiving commands?')
                return 
    
            out, err = pickle.loads(cmd_received)
            if (out): print(out)
            if (err): print(err)
            
            print('Client is running command')
            self.clientSocket.settimeout(None)
            codeOut = self.clientSocket.recv(shell.BUFFER_SIZE) ## might be a long command
            self.clientSocket.settimeout(shell.DEFAULT_TIMEOUT)

            out, err = pickle.loads(codeOut)  ## decode output list
            if (out): print(out)
            if (err): print(err)
            print('Command Complete')

        except AttributeError as e:
            print_err('Error when sending command:' + str(par))
            print(e)
            return 
        except ConnectionResetError:
            print_err('Connection reset')
            return 
  

    def do_close(self, par):
        self.socket.close()

        codeOut = self.socket.recv(self.BUFFER_SIZE)
        out, err = pickle.loads(codeOut)  ## decode output list
        if (out): print(out,end='')
        if (err): print(err,file=sys.stderr,end='')


if __name__ == '__main__':

    pars = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    pars.add_argument("-m", "--mode", nargs='?', type=int, choices=[0, 1, 2],
                      help='Choose modes\nMode 0: local run\nMode 1: server\nMode 2: client')
    pars.add_argument('-i', '--ip', default='127.0.0.1', help='IP of the server')
    args = pars.parse_args()
    mode = args.mode
    if (mode is None):
        print("Choose Server or Client Mode:")
        print("Press 1 to Server and 2 to Client")
        print("Press ENTER to run locally")
        print("Press q to exit")

        while True:
            mode = input("Mode: ")
            #mode = '2'
            if (not mode or mode.isspace() ):
                mode = '0'
                break
            elif (mode.isdecimal()):
                if (int(mode)>=0 or int(mode)<=2):
                    #print(f'Open {modes[int(mode)-1]} Shell')
                    break
            elif mode == 'q' or bool(match(mode, 'qqq+')):
                exit()

    if (int(mode)==1): 
        serverShell().cmdloop()
    elif (int(mode)==2): 
        clientShell(args.ip).cmdloop()
    else: 
        shell().cmdloop()

