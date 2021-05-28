import curses
from curses import wrapper
from newportxps import NewportXPS
import time

newxps = NewportXPS('192.168.0.254', username='xxxxxxxx', password='xxxxxxxxx')
conxps = newxps._xps  # Stands for condensed xps name since newxps._xps is tedious to write

# Group1: IMS500CCHA
# Group2: IMS500CC
# Group3: PR50CC

print()
print('Status: Set Max Velocity')  # unit: mm/s
newxps.set_velocity('Group1.Pos', 5)
time.sleep(5)

print()
print('Status: Set the Initial position')
# Initial Conditions for Stage 1
newxps.move_stage('Group1.Pos', 8)
time.sleep(5)


def main(stdscr):
    stdscr = curses.initscr()
    stdscr.clear()
    count = 1
    stdscr.addstr(0, 0, 'Current Loop Number {}'.format(count))
    stdscr.addstr(1, 0, f"There are currently 5 loops.")
    stdscr.addstr(2, 0, f"This code is not interactive.")
    for i in range(5):
        newxps.move_stage('Group1.Pos', 492)
        newxps.move_stage('Group1.Pos', 8)
        count += 1
        stdscr.addstr(0, 0, 'Current Loop Number {}'.format(count))
        stdscr.addstr(1, 0, f"There are currently 5 loops.")
        stdscr.addstr(2, 0, f"This code is not interactive.")
        stdscr.refresh()


wrapper(main)
