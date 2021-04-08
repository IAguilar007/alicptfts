import sys
from enum import Enum
import os

projpath = os.getcwd()
projpath = projpath.split('alicptfts')[0] + 'alicptfts'

sys.path.append(projpath+'\lib')
sys.path.append(projpath)

import clr
import System
import os
import time
from collections import OrderedDict
from configparser import ConfigParser
#from sftpwrapper import SFTPWrapper
#import sftpwrapper


import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")


# import pythonnet
from System import  Array
from System.Collections import *
clr.AddReference(r'Newport.XPS.CommandInterface')
from CommandInterfaceXPS import *
import numpy as np

print('load assembly')

# reference code: XPS Unified Programmer's Manual.pdf, p9
myXPS = XPS()
op = 0

# op = myXPS.OpenInstrument(host, port,timeout)
hostIP = '192.168.254.254'
op = myXPS.OpenInstrument(hostIP, 5001, 1000)
if (op != 0): raise ValueError('Error: Could not open XPS for test\nError code: {}'.format(op))
else: print("Status: connecting to the XPS controller")

# reference code: XPS Unified Programmer's Manual.pdf, Ch.9
op = myXPS.Login('Administrator','Administrator','DUMMY') ## not sure whether it's required
if (op != 0): raise ValueError('Error: Could login\nError code: {}'.format(op))
else: print("Status: Login XPS")

op = myXPS.KillAll('DUMMY')
if (op != 0): raise ValueError('Error: Could reset group status\nError code: {}'.format(op))
else: print("Status: Reset All Groups")

# group: XPS Unified Programmer's Manual.pdf, Ch.5
op = myXPS.GroupInitialize('SingleAxis','DUMMY')
op = myXPS.GroupHomeSearch('SingleAxis','DUMMY')
if (op != 0): raise ValueError('Error: Cannot initialize group\nError code: {}'.format(op))
else: print('Status: Initialize group')

pos1 = Array[float]([0,0])
op = mmyXPS.GroupMoveAbsolute('SingleAxis',pos1,1,'DUMMY')
if (op != 0): raise ValueError('GroupMoveAbsolute Error\nError code: {}'.format(op))
else: print('Status: Reset the position to origin')
'''
Open XPS Connection
% Connect to the XPS controller
code=myxps.OpenInstrument('192.168.254.254',5001,1000);
Call XPS Functions
% Use API's
[code Version]=myxps.FirmwareVersionGet [code]=myxps.GroupKill('Group1')
[code]=myxps.GroupInitialize('Group1')
[code]=myxps.GroupHomeSearch('Group1')
Close XPS Connection
% Disconnect from the XPS controller
code=myxps.CloseInstrument;

'''
pos2 = Array[float]([100,0])
op = mmyXPS.GroupMoveRelative('SingleAxis',pos2,1,'DUMMY')
if (op != 0): raise ValueError('GroupMoveRelative Error\nError code: {}'.format(op))
else: print('Status: move to +100 mm')
op = myXPS.CloseInstrument()
if (op != 0): raise ValueError('Error: Failure to close XPS\nError code: {}'.format(op))
else: print('Status: Close Connection\nTest Finish')