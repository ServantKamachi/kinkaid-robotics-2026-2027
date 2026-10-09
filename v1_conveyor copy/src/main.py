# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       dannasun, lucas                                              #
# 	Created:      9/10/2026, 8:41:21 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *
import time

brain = Brain()
controller_1 = Controller(PRIMARY)

left_front_dt = Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
left_back_dt = Motor(Ports.PORT9, GearSetting.RATIO_18_1, True)
left_dt = MotorGroup(left_front_dt,left_back_dt)

right_front_dt = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
right_back_dt = Motor(Ports.PORT19, GearSetting.RATIO_18_1, False)
right_dt = MotorGroup(right_front_dt,right_back_dt)

left_arm_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
right_arm_motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
arm_group = MotorGroup(right_arm_motor, left_arm_motor)

left_claw_motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_claw_motor = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
claw_group = MotorGroup(left_claw_motor, right_claw_motor)

gyro = Inertial(Ports.PORT11)

drivetrain = SmartDrive(left_dt, right_dt, gyro, externalGearRatio=5/3)

def PID_drive(distance_mm, heading, velocity, kP, kI, kD):
    global start_integral, start_derivative
    
    #constants, currently broad placeholders

    wheel_diameter = 800 #in mm
    gear_ratio = 5/3

    #calculations
    mm_per_degree = (3.14159 * wheel_diameter) / (360 * gear_ratio)

    distance_degrees = distance_mm / mm_per_degree

    threshold = 0.25
    threshold *= mm_per_degree

    target_mm = distance_mm
    current_mm = 0



    left_dt.set_position(0, DEGREES)
    right_dt.set_position(0, DEGREES)

    integral = start_integral
    derivative = start_derivative
    previousError = 0

    if velocity >= 0:

        target_with_threshold = target_mm - threshold

        while current_mm < target_with_threshold:
            left_pos_degrees = left_dt.position(DEGREES)
            right_pos_degrees = right_dt.position(DEGREES)

            avg_pos_degrees = (left_pos_degrees + right_pos_degrees) / 2.0
            current_mm = avg_pos_degrees * mm_per_degree

            error = heading - gyro.rotation()

            integral += error
            integral = max(min(integral, 50), -50)

            derivative = error - previousError
            derivative = max(min(derivative, 50), -50)

            output = (kP * error) + (kI * integral) + (kD * derivative)

            distance_remaining = target_mm - current_mm
            if distance_remaining < 50:
                slowdown_factor = distance_remaining / 50.0
                adjusted_velocity = velocity * min(1.0, slowdown_factor)
                left_vel = (adjusted_velocity + output)
                right_vel = (adjusted_velocity - output)
            else:
                left_vel = (velocity + output)
                right_vel = (velocity - output)

            left_dt.set_velocity(left_vel, units=PERCENT)
            right_dt.set_velocity(right_vel, units=PERCENT)
            left_dt.spin(FORWARD)
            right_dt.spin(FORWARD)

            previousError = error
            wait(20, MSEC)


    else:

        target_with_threshold = target_mm + threshold  # Negative target
        
        while current_mm > target_with_threshold:
            # Calculate current position in mm
            left_pos_degrees = left_dt.position(DEGREES)
            right_pos_degrees = right_dt.position(DEGREES)
            
            avg_pos_degrees = (left_pos_degrees + right_pos_degrees) / 2.0
            current_mm = avg_pos_degrees * mm_per_degree
            
            # set error
            error = heading - gyro.rotation()

            # update integral
            integral += error
            integral = max(min(integral, 50), -50)

            # update derivative
            derivative = error - previousError
            derivative = max(min(derivative, 50), -50)

            #set velocities
            output = (kP * error) + (kI * integral) + (kD * derivative)
            
            # Slow down as we approach target
            distance_remaining = abs(target_mm - current_mm)
            if distance_remaining < 50:
                slowdown_factor = distance_remaining / 50.0
                adjusted_velocity = velocity * min(1.0, slowdown_factor)
                left_vel = (adjusted_velocity + output)
                right_vel = (adjusted_velocity - output)
            else:
                left_vel = (velocity + output)
                right_vel = (velocity - output)

            left_dt.set_velocity(left_vel, units=PERCENT)
            right_dt.set_velocity(right_vel, units=PERCENT)
            left_dt.spin(FORWARD)
            right_dt.spin(FORWARD)

            previousError = error
            wait(20, MSEC)
    left_dt.stop()
    right_dt.stop()


def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    gyro.calibrate()
    PID_drive(660, 0, 75, 0.2, 0.01, 0.01) #660 mm, at 0°, velocity 75%
    drivetrain.turn_to_rotation(45)
    arm_group.spin_for(REVERSE, 1, SECONDS)
    claw_group.spin_for(REVERSE, 1, SECONDS)

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

        if controller_1.buttonL1.pressing():
            claw_group.spin(FORWARD)
        elif controller_1.buttonL2.pressing():
            claw_group.spin(REVERSE)
        else:
            claw_group.stop(BRAKE)


# create competition instance
comp = Competition(user_control, autonomous)

def controller_stats_update():
    while True:
        #print temps
        controller_1.screen.clear_screen()
        controller_1.screen.set_cursor(1, 1)
        controller_1.screen.print("L: " + str(left_front_dt.temperature()) + " " + str(left_back_dt.temperature()) + " " + "R: " + str(right_front_dt.temperature()) + " " + str(right_back_dt.temperature()))
        
        # #print rpms
        # controller_1.screen.set_cursor(2, 1)
        # controller_1.screen.print("I: " + str(int(intake.velocity())) + " " + "F: " + str(int(flywheel.velocity())) +" " + "C: " + str(int(conveyor.velocity())))
        
        # #drivetrain rpms
        # controller_1.screen.set_cursor(3, 1)
        # controller_1.screen.print("L: " + str(int(leftDtOne.velocity())) + " " + str(int(leftDtTwo.velocity())) + " " + "R: " + str(int(right_dt_one.velocity())) + " " + str(int(right_dt_two.velocity())))
        # wait(500)

# actions to do when the program starts
brain.screen.clear_screen()

def main():
    """
    sets up and updates the UI
    """
    brain.screen.clear_screen()

    # set the text color 
    brain.screen.set_pen_color(Color.WHITE)

    # top right of the screen (where rows and columns are 1-index, NOT zero-indexed!)
    brain.screen.set_cursor(1, 1)
    brain.screen.print("andy needs to read documentation") # print it once for lucas to see 

    # timer for stuff on the UI
    timer = Timer()   

    controller_stats_update()

main()
