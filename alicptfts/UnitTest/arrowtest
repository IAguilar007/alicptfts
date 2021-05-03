from newportxps import NewportXPS
from pynput.keyboard import Listener, Key
import math


xps = NewportXPS('192.168.0.254', username='Administrator', password='Administrator')
xps.initialize_allgroups()
xps.home_allgroups()

# Group1: IMS500CCHA
# Group2: IMS500CC
# Group3: PR50CC

# INITIAL CONDITIONS
length1 = 0 # For Group1, mm
length = 0 # mm
angle = 45.0 # degrees
height = 700 # mm
angle_dependent = True


def center_detector(number):
    ideal_angle = math.degrees(math.atan(height / (math.sqrt(number**2 + height**2) - number)))
    return ideal_angle


def length_boundaries():
    boundary = height / math.tan(math.radians(72))
    return math.trunc(boundary)


print()
print('Check Status: Status should be Ready')
print(xps.status_report())

print()
print('Status: Set Max Velocity')  ## unit: mm/s
xps.set_velocity('Group1.Pos',20)
xps.set_velocity('Group2.Pos',20)
xps.set_velocity('Group3.Pos',10)

print('Status: Set the Initial position')
xps.move_stage('Group1.Pos', length1) # Done near top of code
xps.move_stage('Group2.Pos', length)
xps.move_stage('Group3.Pos', angle)

print('Use Arrow Keys!')
print('Esc button stops exits program!')
print('Space button changes angle dependence. Default True!')


def on_press(key):  # The function that's called when a key is pressed
    global length, angle, angle_dependent
    if key == Key.space: # space button changes whether angle is dependent or not
        angle_dependent = not angle_dependent
        if angle_dependent:
            angle = center_detector(length)
            xps.set_velocity('Group3.Pos', 10)
            xps.move_stage('Group3.Pos', round(angle, 2))
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
        else:
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
    if abs(length) <= length_boundaries():
        if key == Key.right:
            if length != length_boundaries():
                length += 1
            if angle_dependent:
                angle = center_detector(length)
            xps.move_stage('Group2.Pos', length)
            xps.move_stage('Group3.Pos', round(angle, 2))
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
        if key == Key.left:
            if length != - length_boundaries():
                length -= 1
            if angle_dependent:
                angle = center_detector(length)
            xps.move_stage('Group2.Pos', length)
            xps.move_stage('Group3.Pos', round(angle, 2))
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
        if key == Key.up and not angle_dependent:
            angle += .1
            xps.move_stage('Group2.Pos', length)
            xps.move_stage('Group3.Pos', round(angle, 2))
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
        if key == Key.down and not angle_dependent:
            angle -= .1
            xps.move_stage('Group2.Pos', length)
            xps.move_stage('Group3.Pos', round(angle, 2))
            print(f"Angle Dependent: {angle_dependent}.  Position: {length} mm  Angle: {round(angle, 2)}°")
    else:
        length = length_boundaries() if length > 0 else - length_boundaries()
    if key == Key.esc: # Esc button exits
        print('Motion Completed!')
        print()
        print('Status: Print Current Position')
        print('Stage1: {:.2f}'.format(xps.get_stage_position('Group1.Pos')))
        print('Stage2: {:.2f}'.format(xps.get_stage_position('Group2.Pos')))
        print('Stage3: {:.2f}'.format(xps.get_stage_position('Group3.Pos')))
        print()
        print('Test Finish!')
        exit(0)

with Listener(on_press=on_press) as listener:  # Create an instance of Listener
    listener.join()  # Join the listener thread to the main thread to keep waiting for keys

