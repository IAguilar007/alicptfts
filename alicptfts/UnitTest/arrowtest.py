import curses
from curses import wrapper
import math
from newportxps import NewportXPS
import logging
import time

# Setup logging
logging.basicConfig(filename="arrowtest_log.txt", level=logging.DEBUG, format='%(asctime)s %(message)s')

# Changed from xps to newxps since xps is normally an attribute. Making it a class makes it ambiguous
newxps = NewportXPS('192.168.0.254', username='xxxxxxxxxxxxx', password='xxxxxxxxxxxx')
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
print('Status: Set Max Velocity')  # unit: mm/s
newxps.set_velocity('Group1.Pos', 5)
newxps.set_velocity('Group2.Pos', 5)
newxps.set_velocity('Group3.Pos', 5)
time.sleep(5)

print()
print('Status: Set the Initial position')
newxps.move_stage('Group1.Pos', 0)  # Initial Conditions
newxps.move_stage('Group2.Pos', 250)
newxps.move_stage('Group3.Pos', 45)
time.sleep(5)


def clamp(length, height):
    upper_boundary = 250 + height / math.tan(math.radians(72))
    lower_boundary = 250 + height / math.tan(math.radians(108))
    return math.trunc(max(min(length, upper_boundary), lower_boundary))


def center_detector(number, height):
    ideal_angle = math.degrees(math.atan(height / (math.sqrt((number - 250) ** 2 + height ** 2) + number - 250)))
    return ideal_angle


def main(stdscr):
    stdscr = curses.initscr()
    stdscr.clear()
    length = 250
    height = 700
    angle = 45
    vel = 0
    MAX_VELOCITY = 10
    arrow_down = 258
    arrow_up = 259
    arrow_left = 260
    arrow_right = 261
    angle_independent = False
    velocity = False
    stdscr.addstr(0, 0, 'Stage1: {:2f} mm Stage2: {:2f} mm Stage3: {:2f}°'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
    stdscr.addstr(1, 0, f"Press arrow keys for velocity") if velocity else stdscr.addstr(1, 0, f"Press arrow keys for motion")
    stdscr.addstr(2, 0, f"Press 'q' to quit the program")
    stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
    stdscr.addstr(4, 0, f"Press 'c' to change between velocity and position for arrow keys. Currently unavailable.")
    stdscr.addstr(5, 0, f"Mode: Independent angle") if angle_independent else stdscr.addstr(5, 0, f"Mode: Dependent angle")
    newxps.move_stage('Group1.Pos', 492)
    newxps.move_stage('Group1.Pos', 8)
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
        elif ch == arrow_down and angle_independent:
            angle -= 5
        elif ch == arrow_up and angle_independent:
            angle += 5
        elif ch == arrow_left and not velocity:
            if length == clamp(length + 25, height):
                stdscr.addstr(6, 0, "Can't go any more leftwards!")
            length = clamp(length + 25, height)
            if not angle_independent:
                angle = center_detector(length, height)
        elif ch == arrow_right and not velocity:
            if length == clamp(length - 25, height):
                stdscr.addstr(6, 0, "Can't go any more rightwards!")
            length = clamp(length - 25, height)
            if not angle_independent:
                angle = center_detector(length, height)
        elif ch == ord('t'):
            angle_independent = not angle_independent
            if not angle_independent:
                angle = center_detector(length, height)
        elif ch == ord('c'):
            velocity = not velocity
        else:
            pass
        newxps.move_stage('Group2.Pos', length)
        newxps.move_stage('Group3.Pos', angle)
        logging.info('Stage1: {:2f} Stage2: {:2f} Stage3: {:2f}'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
        stdscr.addstr(0, 0, 'Stage1: {:2f} mm Stage2: {:2f} mm Stage3: {:2f}°'.format(newxps.get_stage_position('Group1.Pos'), newxps.get_stage_position('Group2.Pos'), newxps.get_stage_position('Group3.Pos')))
        stdscr.addstr(1, 0, f"Press arrow keys for velocity") if velocity else stdscr.addstr(1, 0, f"Press arrow keys for motion")
        stdscr.addstr(2, 0, f"Press 'q' to quit the program")
        stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
        stdscr.addstr(4, 0, f"Press 'c' to change between velocity and position for arrow keys. Currently unavailable.")
        stdscr.addstr(5, 0, f"Mode: Independent angle") if angle_independent else stdscr.addstr(5, 0, f"Mode: Dependent angle")
        stdscr.refresh()


wrapper(main)
