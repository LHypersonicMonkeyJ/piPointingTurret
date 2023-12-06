import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from horizons import Horizons
from az_el import AzEl
from lktech_motor import LKTECH_Motor
from bmm150 import * # magnetometer

# Variable Initializations
target = 'Sun'

# Class Initializations
horizons = Horizons()
motor_az = LKTECH_Motor(can_id=0x0141, bitrate=250000, timeout=5, motor_model='MS4010-CAN_az') #timeout unit is ms
motor_el = LKTECH_Motor(can_id=0x0142, bitrate=250000, timeout=5, motor_model='MS4010-CAN_el') #timeout unit is ms

# Get target azimuth and elevation from Horizons
horizons.request_ephemeris(target)

# Initialize azimuth and elevation motor positions

# Compute loop delta time
az_el = AzEl(horizons.ephemeris_file_path)
# motor speed per minute
az_rate = az_el.current_azimuth_rate * 60
el_rate = az_el.current_elevation_rate * 60


# Infinite loop until user quits
while True:
    # Get current azimuth and elevation from Horizons
    az_el = AzEl(horizons.ephemeris_file_path)
    print("Current azimuth is: {}".format(az_el.current_azimuth))
    print("Current elevation is: {}".format(az_el.current_elevation))
    print("Current azimuth rate is: {}".format(az_el.current_azimuth_rate))
    print("Current elevation rate is: {}".format(az_el.current_elevation_rate))

    # Calcualte angle position for each motor

    # Send commands to motors

    # Test
    # status = motor1.turn_on_motor()
    # time.sleep(2)
    # status = motor1.turn_off_motor()
    # time.sleep(2)
    #status = motor1.turn_on_motor()
    # time.sleep(2) #delay for 500ms
    #status = motor1.write_current_pos_as_zero_pos_in_ROM()
    #time.sleep(0.5) #delay for 500ms
    #status = motor1.write_current_pos_as_zero_pos_in_ROM()
    status = motor_az.move_angle_speed(180, 360)
    #time.sleep(2)
    #angle = motor_az.read_multi_angle()
    #print("Angle: {}".format(angle))
    #time.sleep(2)
    status = motor_az.move_angle_speed(0, 360)
    #time.sleep(2)
    #angle = motor_az.read_multi_angle()
    #print("Angle: {}".format(angle))
    time.sleep(2)

