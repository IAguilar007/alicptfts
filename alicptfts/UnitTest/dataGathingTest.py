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
#print('Status: Define Trajectory ('+groupname+'.'+pos+')')
dataCol = xps._xps.GatheringListGet(xps._sid)
print('Data record variables:')
print(dataCol)
xps._xps.GatheringConfigurationSet(dataCol)
xps.move_stage('Group1.Pos',250)

print('Status: Finish config setting')
xps._xps.GatheringRun(xps._sid,100,8)
xps.move_stage('Group1.Pos',150,1)

print('Status: Stop gathering')
xps._xps.GatheringStop(xps._sid)
print('Status: Saving')
xps._xps.GatheringStopAndSave(xps._sid)

print()
print('Test Finish!')
