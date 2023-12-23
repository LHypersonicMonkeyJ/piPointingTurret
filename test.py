import os
import sys
import time
import can
from datetime import datetime

#from smbus2 import SMBus
from bme280 import BME280

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
BMM150_I2C_ADDRESS       = 0x13   # (CSB:1 SDO:1) default i2c address
# BME280
BME280_I2C_ADDRESS = 0x77
# MS4010 Motor
MOTOR_ANGLE_RESOLUTION = 0.4 # degree

# Class Initializations
horizons = Horizons()
motor_az = LKTECH_Motor(can_id=0x0141, bitrate=250000, timeout=3, motor_model='MS4010-CAN_az') #timeout unit is ms
motor_el = LKTECH_Motor(can_id=0x0142, bitrate=250000, timeout=3, motor_model='MS4010-CAN_el') #timeout unit is ms
bmm150 = bmm150_I2C(I2C_BUS, BMM150_I2C_ADDRESS)
bme280 = BME280(i2c_addr = BME280_I2C_ADDRESS)

# Initiazlie BMM150
while bmm150.ERROR == bmm150.sensor_init():
    print("sensor init error, please check connect") 
    time.sleep(1)
bmm150.set_operation_mode(bmm150.POWERMODE_NORMAL)
bmm150.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
bmm150.set_rate(bmm150.RATE_10HZ)
bmm150.set_measurement_xyz()
print("BMM150 is ready.")

# Initialize BME280
# workaround to get rid of the first 3 readings
for i in range(3):
    altitude = bme280.get_altitude()
    # print("Altitude is: {}".format(altitude))
    room_temp = bme280.get_temperature()
    room_humidity = bme280.get_humidity()
    time.sleep(0.5)
print("BME280 is ready.")

# Get target azimuth and elevation from Horizons
horizons.request_ephemeris(target)

# Initialize device azimuth and altitude
device_azimuth = bmm150.get_compass_degree()
print("Device azimuth is: {}".format(device_azimuth))

longitude = float(horizons.get_my_location()['longitude'])
latitude = float(horizons.get_my_location()['latitude'])
altitude = float(horizons.get_my_location()['altitude'])
print("Current ip location is: Lat: {:.5f}, Long: {:.5f}, Alt: {:.5f}"
      .format(longitude, latitude, altitude))
sealevel_pressure, outdoor_temp, outdoor_max_temp, outdoor_min_temp, outdoor_humidity = myutils.get_outdoor_weather(longitude, latitude)
print("Sealevel pressure: {} hpa".format(sealevel_pressure))
print("Outdoor temperature: {:.4f} deg F".format(outdoor_temp))
print("Outdoor max temperature: {:.4f} deg F".format(outdoor_max_temp))
print("Outdoor min temperature: {:.4f} deg F".format(outdoor_min_temp))
print("Outdoor humidity: {:.4f} %".format(outdoor_humidity))

# Initialize azimuth and elevation motor positions
# Assumming pointing device is sitting in the local plane that is perpendicular
# to the local gravity vector.
status = motor_az.turn_on_motor()
status = motor_el.turn_on_motor()
status = motor_az.move_angle_speed(0, 360)
status = motor_el.move_angle_speed(0, 360)
azimuth_measurement_is_stable = False
azimuth_buffer = []
buffer_limit = 100
window_size = 5
threshold = 0.2

azimuth_buffer.append(device_azimuth)
while not azimuth_measurement_is_stable and len(azimuth_buffer) < buffer_limit:
    device_azimuth = bmm150.get_compass_degree()
    print("Device azimuth is: {}".format(device_azimuth))
    azimuth_buffer.append(device_azimuth)
    if len(azimuth_buffer) > window_size:
        if myutils.is_steady_state(azimuth_buffer, window_size, threshold):
            azimuth_measurement_is_stable = True
            print("Device azimuth is: {}".format(device_azimuth))
    time.sleep(0.2)
if not azimuth_measurement_is_stable:
    print("Failed to measure device azimuth.")
initial_elevation = 0
initial_motor_speed = 360 # degrees per second
status = motor_az.move_angle_speed(device_azimuth, initial_motor_speed)

# Compute pointing loop delta time in seconds
az_el = AzEl(horizons.ephemeris_file_path)
az_daily_rate = az_el.get_daily_azimuth_rate() #Angle per second
el_daily_rate = az_el.get_daily_elevation_rate() #Angle per second
print("Daily azimuth rate is: {}".format(az_daily_rate))
print("Daily elevation rate is: {}".format(el_daily_rate))
daily_rate = max(az_daily_rate, el_daily_rate) #Angle per second
# make sure loop delta time is sufficient for motor to move at least the resolution
loop_delta_time = MOTOR_ANGLE_RESOLUTION / daily_rate #seconds
# max pointing loop delta time is 30 minutes
loop_delta_time_max = 30 * 60
# min pointing loop delta time is 0.1 seconds
loop_delta_time_min = 0.1
#temp = max(loop_delta_time, loop_delta_time_min)
loop_delta_time = min(max(loop_delta_time, loop_delta_time_min), loop_delta_time_max)
print("Pointing loop delta time is: {} seconds".format(loop_delta_time))

# Motor motor to initial position
az_el.get_az_el(datetime.now())
status = motor_az.move_angle_speed(az_el.get_current_azimuth(), 360)
status = motor_el.move_angle_speed(az_el.get_current_elevation(), 360)
    
# Get start time in seconds that is used to calculate the loop delta time
timestamp_point = time.time()

# Infinite loop until user quits
while True:
    # Get current time in seconds
    current_time = time.time()
    
    # Motor pointing loop
    if current_time - timestamp_point >= loop_delta_time:
        # Get current azimuth and elevation from Horizons
        az_el.get_az_el(datetime.now())
        # print("Current azimuth is: {}".format(az_el.current_azimuth))
        # print("Current elevation is: {}".format(az_el.current_elevation))
        # print("Current azimuth rate is: {}".format(az_el.current_azimuth_rate))
        # print("Current elevation rate is: {}".format(az_el.current_elevation_rate))
        # Calcualte angle position for each motor
        # Send commands to motors
        status = motor_az.move_angle_speed(az_el.get_current_azimuth(), 360)
        status = motor_el.move_angle_speed(az_el.get_current_elevation(), 360)
        # Update timestamp_point
        timestamp_point = current_time
        
    time.sleep(0.5)

