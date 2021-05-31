import curses
from curses import wrapper
import math
from newportxps import NewportXPS
import logging
import time

# Setup logging
logging.basicConfig(filename="accel_log.txt", level=logging.DEBUG, format='%(asctime)s %(message)s')

# Changed from xps to newxps since xps is normally an attribute. Making it a class makes it ambiguous
newxps = NewportXPS('192.168.0.254', username='xxxxxxxxx', password='xxxxxxxxxx')
conxps = newxps._xps  # Stands for condensed xps name since newxps._xps is tedious to write
socketId = conxps.TCP_ConnectToServer('171.64.56.87', 5001, 20)
newxps.initialize_allgroups()
newxps.home_allgroups()

# Group1: IMS500CCHA
# Group2: IMS500CC
# Group3: PR50CC

print()
print('Check Status: Status should be Ready')
print(newxps.status_report())
time.sleep(5)

print()
print('Now please start move_stage1.py in another terminal.')
time.sleep(20)

print()
print('Status: Set Max Velocity')  # unit: mm/s
newxps.set_velocity('Group2.Pos', 5)
newxps.set_velocity('Group3.Pos', 20)
time.sleep(5)

print()
print('Status: Set the Initial position')
# Initial Conditions for Stage 2 and Stage 3
newxps.move_stage('Group2.Pos', 250)
newxps.move_stage('Group3.Pos', 45)
time.sleep(5)


def upper_bound(height):
    upper_boundary = 250 + height / math.tan(math.radians(72))
    return upper_boundary


def lower_bound(height):
    lower_boundary = 250 + height / math.tan(math.radians(108))
    return lower_boundary


def clamp(length, height):
    return math.trunc(max(min(length, upper_bound(height)), lower_bound(height)))


def center_detector(number, height):
    ideal_angle = math.degrees(math.atan(height / (math.sqrt((number - 250) ** 2 + height ** 2) + number - 250)))
    return ideal_angle


def main(stdscr):
    stdscr = curses.initscr()
    stdscr.clear()
    length = 250
    height = 700
    angle = 45
    velocity = 5
    max_velocity = 20
    acceleration_bool = False
    acceleration = 5
    max_acceleration = 20
    arrow_down = 258
    arrow_up = 259
    arrow_left = 260
    arrow_right = 261
    angle_independent = False
    stdscr.addstr(0, 0, 'Stage1: {:2f} mm Stage2: {:2f} mm Stage3: {:2f}°'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
    stdscr.addstr(1, 0, f"Press left/right arrow keys for acceleration") if acceleration_bool else stdscr.addstr(1, 0, f"Press left/right arrow keys for velocity")
    stdscr.addstr(2, 0, f"Press 'q' to quit the program")
    stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
    stdscr.addstr(4, 0, f"Mode: Independent angle. Up/Down arrow keys now available") if angle_independent else stdscr.addstr(4, 0, f"Mode: Dependent angle")
    stdscr.addstr(5, 0, f"Press 'c' to change acceleration and velocity commands")
    while True:
        ch = stdscr.getch()
        stdscr.clear()
        if ch == ord('q'):
            conxps.KillAll(socketId)
            conxps.TCP_CloseSocket(socketId)
            stdscr.addstr(0, 0, "Test Completed")
            stdscr.refresh()
            time.sleep(5)
            break
        if newxps.get_stage_position('Group2.Pos') >= upper_bound(height):
            newxps.move_stage('Group2.Pos', lower_bound(height) + 1)
        if newxps.get_stage_position('Group2.Pos') <= lower_bound(height):
            newxps.move_stage('Group2.Pos', upper_bound(height) - 1)
        elif not angle_independent:
            angle = center_detector(length, height)
        elif ch == arrow_down and angle_independent:
            angle -= 0.1
        elif ch == arrow_up and angle_independent:
            angle += 0.1
        elif ch == arrow_left:
            if acceleration_bool and acceleration > 0:
                acceleration -= 1
            if not acceleration_bool and velocity > 0:
                velocity -= 1
        elif ch == arrow_right:
            if acceleration_bool and acceleration < max_acceleration:
                acceleration += 1
            if not acceleration_bool and velocity < max_velocity:
                velocity += 1
        elif ch == ord('c'):
            acceleration_bool = not acceleration_bool
        elif ch == ord('t'):
            angle_independent = not angle_independent
        else:
            pass
        newxps.set_velocity('Group1.Pos', velocity, acceleration)
        newxps.move_stage('Group3,Pos', angle)
        logging.info('Stage1: {:2f} Stage2: {:2f} Stage3: {:2f}'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
        stdscr.addstr(0, 0, 'Stage1: {:2f} mm Stage2: {:2f} mm Stage3: {:2f}°'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
        stdscr.addstr(1, 0, f"Press left/right arrow keys for acceleration") if acceleration_bool else stdscr.addstr(1, 0, f"Press left/right arrow keys for velocity")
        stdscr.addstr(2, 0, f"Press 'q' to quit the program")
        stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
        stdscr.addstr(4, 0, f"Mode: Independent angle. Up/Down arrow keys now available") if angle_independent else stdscr.addstr(4, 0, f"Mode: Dependent angle")
        stdscr.addstr(5, 0, f"Press 'c' to change acceleration and velocity commands")
        stdscr.refresh()


wrapper(main)
