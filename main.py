# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       dannasun                                                     #
# 	Created:      9/10/2026, 8:41:21 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

brain = Brain()
controller_1 = Controller(PRIMARY)

left_front_dt = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
left_back_dt = Motor(Ports.PORT9, GearSetting.RATIO_18_1, True)
left_dt = MotorGroup(left_front_dt,left_back_dt)

right_front_dt = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
right_back_dt = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
right_dt = MotorGroup(right_front_dt,right_back_dt)

left_arm_motor = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
right_arm_motor = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
arm_group = MotorGroup(right_arm_motor, left_arm_motor)

drivetrain = DriveTrain(left_dt, right_dt, externalGearRatio=5/3)

def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here

def user_control():
    brain.screen.clear_screen()
    brain.screen.print("driver control")
    # place driver control in this while loop
    while True:
        forward_motion = controller_1.axis3.position()
        turn_motion = controller_1.axis1.position()
        if abs(forward_motion) >= 5 or abs(turn_motion) >= 5:
            left_velocity = forward_motion - turn_motion
            right_velocity = forward_motion + turn_motion

            if left_velocity > 0:
                left_dt.set_velocity(left_velocity, PERCENT)
                left_dt.spin(FORWARD)
            else:
                left_dt.set_velocity(abs(left_velocity), PERCENT)
                left_dt.spin(REVERSE)

            if right_velocity > 0:
                right_dt.set_velocity(right_velocity, PERCENT)
                right_dt.spin(FORWARD)
            else:
                right_dt.set_velocity(abs(right_velocity), PERCENT)
                right_dt.spin(REVERSE)
        else:
            drivetrain.stop()

        if controller_1.buttonR1.pressing():
            arm_group.spin(FORWARD)
        elif controller_1.buttonR2.pressing():
            arm_group.spin(REVERSE)
        else:
            arm_group.stop(HOLD)




# create competition instance
comp = Competition(user_control, autonomous)

# actions to do when the program starts
brain.screen.clear_screen()