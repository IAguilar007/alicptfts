import curses
from curses import wrapper
import math
from newportxps import NewportXPS
import logging
import time
import newportxps.XPS_C8_drivers

# Setup logging
logging.basicConfig(filename="key_log.txt", level=logging.DEBUG, format='%(asctime)s %(message)s')

xps = NewportXPS('192.168.0.254', username='xxxxxxx', password='xxxxxx')
xps.initialize_allgroups()
xps.home_allgroups()

# Group1: IMS500CCHA
# Group2: IMS500CC
# Group3: PR50CC

print()
print('Check Status: Status should be Ready')
print(xps.status_report())
time.sleep(5)

print()
print('Status: Set Max Velocity')  # unit: mm/s
xps.set_velocity('Group1.Pos', 5)
xps.set_velocity('Group2.Pos', 5)
xps.set_velocity('Group3.Pos', 5)
time.sleep(5)

print()
print('Status: Set the Initial position')
xps.move_stage('Group1.Pos', 0)  # Initial Conditions
xps.move_stage('Group2.Pos', 250)
xps.move_stage('Group3.Pos', 45)
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
    arrow_down = 258
    arrow_up = 259
    arrow_left = 260
    arrow_right = 261
    angle_independent = False
    stdscr.addstr(0, 0, f"Position: {round(length, 2)} mm, Angle: {round(angle, 2)}°")
    stdscr.addstr(1, 0, f"Press arrow keys for motion")
    stdscr.addstr(2, 0, f"Press 'q' to quit the program")
    stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
    stdscr.addstr(4, 0, f"Mode: Independent angle") if angle_independent else stdscr.addstr(4, 0, f"Mode: Dependent angle")
    while True:
        ch = stdscr.getch()
        stdscr.clear()
        if ch == ord('q'):
            stdscr.addstr(0, 0, "Test Completed")
            stdscr.refresh()
            xps.KillAll()
            time.sleep(5)
            break
        elif ch == arrow_down and angle_independent:
            angle -= 0.1
        elif ch == arrow_up and angle_independent:
            angle += 0.1
        elif ch == arrow_left:
            if length == clamp(length + 1, height):
                stdscr.addstr(5, 0, "Can't go any more leftwards!")
            length = clamp(length + 1, height)
            if not angle_independent:
                angle = center_detector(length, height)
        elif ch == arrow_right:
            if length == clamp(length - 1, height):
                stdscr.addstr(5, 0, "Can't go any more rightwards!")
            length = clamp(length - 1, height)
            if not angle_independent:
                angle = center_detector(length, height)
        elif ch == ord('t'):
            angle_independent = not angle_independent
            if not angle_independent:
                angle = center_detector(length, height)
        else:
            pass
        xps.move_stage('Group2.Pos', length)
        xps.move_stage('Group3.Pos', angle)
        logging.info('Stage1: {:2f} Stage2: {:2f} Stage3: {:2f}'.format(xps.get_stage_position('Group1.Pos'), xps.get_stage_position('Group2.Pos'), xps.get_stage_position('Group3.Pos')))
        stdscr.addstr(0, 0, 'Stage1: {:2f} mm Stage2: {:2f} mm Stage3: {:2f}°'.format(xps.get_stage_position('Group1.Pos'), xps.get_stage_position('Group2.Pos'), xps.get_stage_position('Group3.Pos')))
        stdscr.addstr(1, 0, f"Press arrow keys for motion")
        stdscr.addstr(2, 0, f"Press 'q' to quit the program")
        stdscr.addstr(3, 0, f"Press 't' to toggle between an independent angle and a dependent angle")
        stdscr.addstr(4, 0, f"Mode: Independent angle") if angle_independent else stdscr.addstr(4, 0, f"Mode: Dependent angle")
        stdscr.refresh()


wrapper(main)
