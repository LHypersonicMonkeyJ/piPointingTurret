import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import myutils
from horizons import Horizons
from az_el import AzEl
from lktech_motor import LKTECH_Motor
from bmm150 import * # magnetometer

# Variable Initializations
target = 'Sun'
# BMM150
I2C_BUS         = 0x01   #default use I2C1
ADDRESS_3       = 0x13   # (CSB:1 SDO:1) default i2c address

# Class Initializations
horizons = Horizons()
motor_az = LKTECH_Motor(can_id=0x0141, bitrate=250000, timeout=5, motor_model='MS4010-CAN_az') #timeout unit is ms
motor_el = LKTECH_Motor(can_id=0x0142, bitrate=250000, timeout=5, motor_model='MS4010-CAN_el') #timeout unit is ms
bmm150 = bmm150_I2C(I2C_BUS, ADDRESS_3)

# Initiazlie BMM150
while bmm150.ERROR == bmm150.sensor_init():
    print("sensor init error, please check connect") 
    time.sleep(1)
bmm150.set_operation_mode(bmm150.POWERMODE_NORMAL)
bmm150.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
bmm150.set_rate(bmm150.RATE_10HZ)
bmm150.set_measurement_xyz()

# Get target azimuth and elevation from Horizons
horizons.request_ephemeris(target)

# Initialize azimuth and elevation motor positions
# Assumming pointing device is sitting in the local plane that is perpendicular
# to the local gravity vector.
azimuth_measurement_is_stable = False
azimuth_buffer = []
buffer_limit = 100
while not azimuth_measurement_is_stable and len(azimuth_buffer) < buffer_limit:
    device_azimuth = bmm150.get_compass_degree()
    azimuth_buffer.append(device_azimuth)
    if myutils.is_steady_state(azimuth_buffer, 5, 0.1):
        azimuth_measurement_is_stable = True
        print("Device azimuth is: {}".format(device_azimuth))
    time.sleep(0.1)
if not azimuth_measurement_is_stable:
    print("Failed to measure device azimuth.")
initial_elevation = 0
initial_motor_speed = 360 # degrees per second
status = motor_az.move_angle_speed(device_azimuth, initial_motor_speed)
status = motor_el.move_angle_speed(initial_elevation, initial_motor_speed)

# # Compute loop delta time
# az_el = AzEl(horizons.ephemeris_file_path)
# # motor speed per minute
# az_rate = az_el.current_azimuth_rate * 60
# el_rate = az_el.current_elevation_rate * 60


# # Infinite loop until user quits
# while True:
#     # Get current azimuth and elevation from Horizons
#     az_el = AzEl(horizons.ephemeris_file_path)
#     print("Current azimuth is: {}".format(az_el.current_azimuth))
#     print("Current elevation is: {}".format(az_el.current_elevation))
#     print("Current azimuth rate is: {}".format(az_el.current_azimuth_rate))
#     print("Current elevation rate is: {}".format(az_el.current_elevation_rate))

#     # Calcualte angle position for each motor

#     # Send commands to motors

#     # Test
#     # status = motor1.turn_on_motor()
#     # time.sleep(2)
#     # status = motor1.turn_off_motor()
#     # time.sleep(2)
#     #status = motor1.turn_on_motor()
#     # time.sleep(2) #delay for 500ms
#     #status = motor1.write_current_pos_as_zero_pos_in_ROM()
#     #time.sleep(0.5) #delay for 500ms
#     #status = motor1.write_current_pos_as_zero_pos_in_ROM()
#     status = motor_az.move_angle_speed(180, 360)
#     #time.sleep(2)
#     #angle = motor_az.read_multi_angle()
#     #print("Angle: {}".format(angle))
#     #time.sleep(2)
#     status = motor_az.move_angle_speed(0, 360)
#     #time.sleep(2)
#     #angle = motor_az.read_multi_angle()
#     #print("Angle: {}".format(angle))
#     time.sleep(2)

