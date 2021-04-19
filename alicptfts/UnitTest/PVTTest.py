from newportxps import NewportXPS

xps = NewportXPS('192.168.254.254', username='Administrator', password='Administrator')
xps.initialize_allgroups()
xps.home_allgroups()

print()
print('Check Status: Status should be Ready')
print(xps.status_report())

# Group1: IMS500CCHA
# Group2: IMS500CC
# Group3: PR50CC
print('Print Hardware Status')
print(xps.get_hardware_status())

print()
groupname = 'Group1'
pos = 'Pos'
print('Status: Define Trajectory ('+groupname+'.'+pos+')')
'''
define_line_trajectories(self, axis, group=None,
                                 start=0, stop=1, step=0.001, scantime=10.0,
                                 accel=None, upload=True, verbose=False):
                                     '''
xps.define_line_trajectories(pos,groupname,150,250,20,10)
print('Status: Running trajectory')
xps.run_trajectory('forward')
# xps.run_trajectory('backward')
xps.download_trajectory('traj.dat')

print()
print('Test Finish!')
