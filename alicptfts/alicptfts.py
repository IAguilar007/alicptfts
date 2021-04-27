#!/usr/bin/env python

import sys
import os
print(os.getcwd())
#import System
#from System import String

sys.path.append(r'../lib')
sys.path.append(r'lib')


#import lib.MC2000B_COMMAND_LIB as mc2000b
# import MC2000B_COMMAND_LIB as mc2000b
from newportxps import NewportXPS
from newportxps.XPS_C8_drivers import XPSException

import enum

class FTSState(enum.Enum):
    NOTINIT  = 0
    INIT     = 1
    CONFIG   = 2
    SCANNING = 3
    PAUSE    = 4
    FINISH   = 5

class FTSmotion(enum.Enum):
    PointingLinear = 0
    PointingRotary = 1
    MovingLinear = 2
    
class MC2000B:
    def __init__(self):
        pass

class IR518:
    def __init__(self):
        pass

class AlicptFTS:
    def __init__(self):
        self.source = None
        self.chopper = None
        self.newportxps = None 
        self.state = FTSState.NOTINIT

    def initialize(self, host='192.168.254.254',username='Administrator',password='Administrator',port=5001, timeout=100):
        """Establish connection with each part.
        
        Parameters
        ----------
        host : string
            IP address of the XPS controller.

        port : int
            Port number of the XPS controller (default is 5001).

        timeout : int
            Receive timeout of the XPS in milliseconds 
            (default is 1000). Note that the send timeout is 
            set to 1000 milliseconds. See the XPS Programming 
            Manual.

        username : string (default is Administrator)

        password : string (default is Administrator)
        """
        self.check_state('initialize')

        
        # Current implementation considers only the XPS controller
        self.source = IR518()
        self.chopper = MC2000B()
        if (self.newportxps is None):     # Start a new connection
            try:
                self.newportxps = NewportXPS(host, username, password,port,timeout)
                print(xps.status_report())

            except XPSException:
                print('Cannot Connect to XPS')
                raise
            except:
                print('Unkown System Reason')
                raise
        else:                           # From a reboot
            try:
                print('reboot')
                #self.newportxps.initialize()
                self.newportxps.connect()      # not tested
            except Exception:
                pass

        print('STATUS: Initialize all groups')
        self.newportxps.initialize_allgroups()
        print(xps.status_report())
        print('STATUS: Initialize all groups')
        self.newportxps.home_allgroups()
        print(xps.status_report())
        self.state = FTSState.INIT

    def configure(self, positions, relative=False):
        """Configure the stages so that the FTS is ready to scan.
        
        One my wish to modify the motion params before configuring
        the pointing mirror. In that case, call the set_motion_params
        function, e.g.,
        self.set_motion_params('PointingLinear', params_lin)
        self.set_motion_params('PointingRotary', params_rot)

        Parameters
        ----------
        positions : array of float
            Target coordinates of the pointing mirror in (position, angle).

        relative : bool
            If relative is True, the pointing mirror is configured to the
            original coordinates plus "positions" (default is False).
        """
        self.check_state('configure')

        try:
            self.newportxps.configure_pointing(positions=positions, relative=relative)
        except XPSException:
            pass
        except Exception:
            pass

        self.state = FTSState.CONFIG

    def scan(self, scan_params=None, scan_range=None, repeat=15):
        """Perform a scan with the configured stages.
        
        Parameters
        ----------
        scan_params : array of float, optional
            Scan parameters for the SGamma profile (see Newport XPS-D
            feature manual pp. 8-9). Use format
            [vel, acc, min_jerk_time, max_jerk_time]. Simply put the not-
            interested parameters as "None". In that case, the default
            value (or value set by an previous operation) will be used.
            Will use default values if not specificed (None).
    
        scan_range : array of float, optional
            Minimum and maximum target positions. Use format 
            [min_target, max_target].
            Will use default values if not specified (None).

        repeat : int
            Number of full back-and-forth scans (default is 15).
        """
        self.check_state('scan')
        try:
            self.set_motion_params('MovingLinear', scan_params)
        except Exception:
            pass
        
        self.state = FTSState.SCANNING
        try:
            timestamps = self.newportxps.scan(scan_range=scan_range, repeat=repeat)
        except XPSException:
            pass
        except Exception:
            self.state = FTSState.NOTINIT
            pass
        else:
            self.state = FTSState.FINISH
            return timestamps

    def save(self, timestamps=None, tname='TIMESTAMPS.DAT', fname='GATHERING.DAT'):
        """Save the gathering data and timestamps after a scan.
        
        Parameters
        ----------
        timestamps: array of float
            Timestamps for data points reported by the "scan()" 
            function. If None, then no timestamps will be saved.

        tname: string
            Name of the file storing the timestamps (default is
            'TIMESTAMPS.DAT'). Can specify absolute path.

        fname: string
            Name of the file storing the gathering data, including
            encoder positions and velocities (default is 
            'GATHEIRNG.DAT'). Can specify absolute path.
        """
        self.check_state('save')
        try:
            self.newportxps.save_gathering(fname)
        except Exception:
            pass

        if timestamps is not None:
            try:
                self.save_timestamps(timestamps, tname)
            except Exception:
                pass

    def reboot(self):
        """Reboot the system to the NOTINIT state"""
        self.check_state('reboot')
        try:
            self.newportxps.reboot(reconnect=False, timeout=120.0)
        except Exception:
            pass

    def stop(self):
        """Abort any ongoing motions
        
        Bring the system back to the NOTINIT state. Applicable when
        the system is in the CONFIG or the SCANNING states.
        """
        self.check_state('stop')
        try:
            #self.newportxps.stop_all()
            self.newportxps._xps.KillAll(self.newportxps._sid)
        except Exception:
            pass
    
    def pause(self):
        """Temporarily hold the system from further actions
        
        Applicable when the system is in the CONFIG state.
        """
        self.check_state('pause')
        try:
            self.newportxps.abort_group('Group1')  # Group name is not determined
        except Exception:
            pass

    def resume(self):
        """Bring the paused system back to the CONFIG state"""
        self.check_state('resume')
        try:
            self.newportxps.resume_all()
        except Exception:
            pass

    def status(self):
        try:
            self.check_state('status')
        except Exception:
            pass
        try:
            status_report = self.newportxps.status_report()
            print(status_report)
        except Exception:
            pass

    def close(self):
        """Close the instrument (socket of the XPS)"""
        try:
            self.check_state('close')
        except Exception:
            pass
        try:             # copy from reboot function
            self.newportxps.ftpconn.close()
            self.newportxps._xps.CloseAllOtherSockets(self.newportxps._sid)
        except Exception:
            pass

    ## Helper functions
    def save_timestamps(self, timestamps, tname):
        try:
            np.savetxt(tname, np.array(timestamps), delimiter=' ')
        except Exception:
            raise

    # TODO
    # We might want to promote this function to a command
    # if it turns out to be useful during the operation
    def set_motion_params(self, xps_grp, params):
        """Set the SGamma profile parameters for an XPS positioner
        
        Parameters
        ----------
        xps_grp : string
            One of the following: PointingLinear, PointingRotary,
            and MovingLinear.

        scan_params : array of float
            Scan parameters for the SGamma profile in
            [vel, acc, min_jerk_time, max_jerk_time]. Simply put the not-
            interested parameters as "None".
            Will use default values if not specificed (None).
        """
        self.check_state('set_motion_params')
        try:
            self.newportxps.set_motion_params(xps_grp, params)
        except Exception:
            pass

    ## TODO
    def check_state(self, command):
        if command == 'initialize': pass
        elif command == 'configure': pass
        elif command == 'scan': pass
        elif command == 'save': pass
        elif command == 'reboot': pass
        elif command == 'stop': pass
        elif command == 'pause': pass
        elif command == 'resume': pass
        elif command == 'status': pass
        elif command == 'close': pass
        else:
            raise ValueError('Error: Invalid command')

if __name__ == '__main__':
    fts = AlicptFTS()
    fts.initialize('192.168.0.254','Administrator','Administrator')
    print('Status: Finish initialization')
    fts.status()
    print('Test REBOOT')
    fts.reboot()
    fts.status()
    print('Test Finished')
    print('Disconnect...')
    fts.close()
    print('Done')




    '''
    fts = AlicptFTS()
    fts.initialize()
    fts.status()
    fts.configure(positions=[50.0, 35.0], relative=False)
    timestamps = fts.scan()
    fts.save(timestamps=timestamps)
    fts.close()
    '''
