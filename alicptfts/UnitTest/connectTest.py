import sys
from enum import Enum
import os
#sys.path.append(r'../lib')
#sys.path.append(r'lib')

projpath = os.getcwd()
projpath = projpath.split('alicptfts')[0] + 'alicptfts'


sys.path.append(projpath+'\lib')
sys.path.append(projpath)
#sys.path.append(r'C:\Users\d3a2s\Source\Repos\shu-xiao\alicptfts\lib')
#sys.path.append(r'C:\Users\d3a2s\Source\Repos\shu-xiao\alicptfts')




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
from System import String
from System.Collections import *
clr.AddReference(r'Newport.XPS.CommandInterface')
from CommandInterfaceXPS import *
print('load assembly')

import numpy as np

# reference code: XPS Unified Programmer's Manual.pdf, p9
myXPS = XPS()
# op = myXPS.OpenInstrument(host, port,timeout)
hostIP = '192.168.254.254'
op = myXPS.OpenInstrument(hostIP, 5001, 1000)

if (op != 0): raise ValueError('Error: Could not open XPS for test\nError code: {}'.format(op))
else: print("Status: connecting to the XPS controller")

# reference code: XPS Unified Programmer's Manual.pdf, Ch.9
myXPS.Login('Administrator','Administrator')  ## not sure whether it's required
op = myXPS.KillAll()
if (op != 0): raise ValueError('Error: Could reset group status\nError code: {}'.format(op))
else: print("Status: Reset All Groups")

# group: XPS Unified Programmer's Manual.pdf, Ch.5
op = myXPS.GroupInitialize('SingleAxis')
op = myXPS.GroupHomeSearch('SingleAxis')
if (op != 0): raise ValueError('Error: Cannot initialize group\nError code: {}'.format(op))
else: print('Status: Initialize group')

op = mmyXPS.GroupMoveAbsolute('SingleAxis',[0,0],1)
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
op = mmyXPS.GroupMoveRelative('SingleAxis',[100,0],1)
if (op != 0): raise ValueError('GroupMoveRelative Error\nError code: {}'.format(op))
else: print('Status: move to +100 mm')
op = myXPS.CloseInstrument()
if (op != 0): raise ValueError('Error: Failure to close XPS\nError code: {}'.format(op))
else: print('Status: Close Connection\nTest Finish')