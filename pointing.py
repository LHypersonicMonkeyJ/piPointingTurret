import os
import sys
import time
import can
from datetime import datetime
from bme280 import BME280
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import myutils
from horizons import Horizons
from az_el import AzEl
from lktech_motor import LKTECH_Motor
from bmm150 import * # magnetometer

# Create a pointing class to handle all pointing related functions
class pointing():
    def __init__(self):
        self.available_targets = ['Sun', 'Moon', 'Mars', 'ISS']
        self.targets_already_selected = dict() #key is target, value is data valid date
        self.current_target = None
        self.az_el = None

        # device variables
        self.device_azimuth = 0 # this will be udpated in the _initialize_sensors function
        self.device_elevation = 0
        self.initial_motor_speed = 360 # degrees per second
        self.bmm150_buffer = [] # buffer to store initial bme280 readings
        self.bmm150_buffer_limit = 100 # buffer limit
        self.bmm150_window_size = 5 # window size for moving average
        self.bmm150_exclude_size = 3 # window_size = 5, so exclude the first 3 readings
        self.bmm150_threshold = 0.75 # stable reading threshold

        # initialize Horizons
        self.horizons = Horizons()
        self.longitude = self.horizons.get_my_longitude()
        self.latitude = self.horizons.get_my_latitude()
        self.altitude = self.horizons.get_my_altitude()

        # initialize sensors
        self._initialize_sensors()

        # initialize weather
        self._initialize_weather()

        # initialize motors
        self._initialize_motors(initial_azimuth = self.device_azimuth,
                                initial_elevation = self.device_elevation, 
                                initial_speed = self.initial_motor_speed)
    
    def _initialize_weather(self):
        self.room_temp = None
        self.room_humidity = None
        self.room_pressure = None
        self.outdoor_sealevel_pressure, \
        self.outdoor_temp, \
        self.outdoor_max_temp, \
        self.outdoor_min_temp, \
        self.outdoor_humidity, \
        self.outdoor_feellike_temp = myutils.get_outdoor_weather(self.longitude, self.latitude)
        
    def _initialize_sensors(self):
        # BMM150
        I2C_BUS                  = 0x01
        BMM150_I2C_ADDRESS       = 0x13
        self.bmm150 = bmm150_I2C(I2C_BUS, BMM150_I2C_ADDRESS)
        while self.bmm150.ERROR == self.bmm150.sensor_init():
            print("sensor init error, please check connect") 
            time.sleep(1)
        self.bmm150.set_operation_mode(self.bmm150.POWERMODE_NORMAL)
        self.bmm150.set_preset_mode(self.bmm150.PRESETMODE_HIGHACCURACY)
        self.bmm150.set_rate(self.bmm150.RATE_10HZ)
        self.bmm150.set_measurement_xyz()

        # get stable bmm150 reading
        flag_bmm150_stable = False
        device_azimuth = self.bmm150.get_compass_degree()

        self.bmm150_buffer.append(device_azimuth)
        while not flag_bmm150_stable and len(self.bmm150_buffer) < self.bmm150_buffer_limit:
            device_azimuth = self.bmm150.get_compass_degree()
            print("Device azimuth measurement: {}".format(device_azimuth))
            self.bmm150_buffer.append(device_azimuth)
            if len(self.bmm150_buffer) > self.bmm150_window_size:
                if myutils.is_steady_state(self.bmm150_buffer, self.bmm150_window_size, self.bmm150_threshold):
                    flag_bmm150_stable = True
                    # Get the average reading of the current buffer exclude the first self.bmm150_exclude_size readings
                    excluded_bmm150_buffer = self.bmm150_buffer[self.bmm150_exclude_size:]
                    self.device_azimuth = sum(excluded_bmm150_buffer) / len(excluded_bmm150_buffer)
                    self.bmm150_buffer = [] # clear buffer
                    print("BMM150 is ready.")
                    print("Device azimuth is initialized to: {}".format(self.device_azimuth))
            time.sleep(0.1)

        if not flag_bmm150_stable:
            # Get the average reading of the buffer exclude the first self.bmm150_window_size readings
            excluded_bmm150_buffer = self.bmm150_buffer[self.bmm150_exclude_size:]
            self.device_azimuth = sum(excluded_bmm150_buffer) / len(excluded_bmm150_buffer)
            self.bmm150_buffer = [] # clear buffer
            print("WARNINGS: BMM150 failed to converge. Device azimuth is set to: {}".format(self.device_azimuth))

        # BME280
        BME280_I2C_ADDRESS = 0x77
        self.bme280 = BME280(i2c_addr = BME280_I2C_ADDRESS)
        # workaround to get rid of the first 3 readings
        for i in range(3):
            altitude = self.bme280.get_altitude()
            # print("Altitude is: {}".format(altitude))
            room_temp = self.bme280.get_temperature()
            room_humidity = self.bme280.get_humidity()
            time.sleep(0.5)
        print("BME280 is ready.")


    def _initialize_motors(self, initial_azimuth, initial_elevation, initial_speed):
        # MS4010 Motor
        MOTOR_ANGLE_RESOLUTION = 0.4
        MOTOR_ANGLE_MIN = 0
        MOTOR_ANGLE_MAX = 360
        BITRATE = 250000
        TIMEOUT = 3
        self.motor_az = LKTECH_Motor(can_id=0x0141, bitrate=BITRATE, 
                                     timeout=TIMEOUT, motor_tag='MS4010-CAN_az') #timeout unit is ms
        self.motor_el = LKTECH_Motor(can_id=0x0142, bitrate=BITRATE,
                                     timeout=TIMEOUT, motor_tag='MS4010-CAN_el')
        # 2 second idle time
        #time.sleep(5)

        if not self.motor_az.turn_on_motor():
            print("ERROR: Failed to turn on azimuth motor")
            return False
        if not self.motor_el.turn_on_motor():
            print("ERROR: Failed to turn on elevation motor")
            return False
        # move motors to 0 positions
        if not self.motor_az.move_angle_speed(0, 360):
            print("ERROR: Failed to move azimuth motor to 0 position")
            return False
        if not self.motor_el.move_angle_speed(0, 360):
            print("ERROR: Failed to move elevation motor to 0 position")
            return False
        
        # move to default initial positions
        status = self.motor_az.move_angle_speed(initial_azimuth, initial_speed)
        if not status:
            print("ERROR: Failed to move azimuth motor to initial position")
            return False
        status = self.motor_el.move_angle_speed(initial_elevation, initial_speed)
        if not status:
            print("ERROR: Failed to move elevation motor to initial position")
            return False
        
        return True

    def reinitialize(self):
        pass

    def update_outdoor_weather(self):
        self.outdoor_sealevel_pressure, \
        self.outdoor_temp, \
        self.outdoor_max_temp, \
        self.outdoor_min_temp, \
        self.outdoor_humidity, \
        self.outdoor_feellike_temp = myutils.get_outdoor_weather(self.longitude, self.latitude)

        if self.outdoor_temp is None:
            return False
        else:
            return True

    def _validate_target(self, target):
        if target in self.available_targets:
            self.target = target
            return True
        else:
            return False
        
    # Public Functions
    #--------------------------------------------------------------------
    # getters and setters
    # get outdoor weather from ip address (should not call this too often)
    def get_outdoor_temp(self):
        # get outdoor temperature from ip address
        return self.outdoor_temp
    
    def get_outdoor_humidity(self):
        # get outdoor humidity from ip address
        return self.outdoor_humidity
    
    def get_outdoor_sealevel_pressure(self):
        # get outdoor sealevel pressure from ip address
        return self.outdoor_sealevel_pressure
    
    def get_outdoor_max_temp(self):
        # get outdoor max temperature from ip address
        return self.outdoor_max_temp
    
    def get_outdoor_min_temp(self):
        # get outdoor min temperature from ip address
        return self.outdoor_min_temp

    def get_outdoor_feellike_temp(self):
        # get outdoor feels like temperature from ip address
        return self.outdoor_feellike_temp
        
    
    # get indoor weather
    def get_indoor_temperature(self):
        temp_celsius = self.bme280.get_temperature()
        temp_fahrenheit = temp_celsius * 9 / 5 + 32
        return temp_fahrenheit
    
    def get_indoor_humidity(self):
        return self.bme280.get_humidity()
    
    def get_indoor_pressure(self):
        return self.bme280.get_pressure()

    # get current target ephermeris from Horizons
    def initialize_target(self, target):
        if not self._validate_target(target):
            warnings.warn("Invalid target: {}".format(target))
            return False
        
        # check to see if the target has already been initialized
        # get current valid time
        current_valid_time = datetime.today().strftime('%Y-%b-%d') + ' UT' + self.utc_offset
        if target in self.targets_already_selected.keys():
            if current_valid_time == self.targets_already_selected[target]:
                # if time is valid then do nothing
                pass
            else:
                # if time is not valid, request new empemeris data and update the target valid time
                target_valid_date = self.horizons.request_ephemeris(target)
                self.targets_already_selected[target] = target_valid_date
        else:
            # target not initialized yet. Need to call for new ephemeris
            target_valid_date = self.horizons.request_ephemeris(target)
            self.targets_already_selected[target] = target_valid_date

        # Initialize az_el object
        self.az_el = AzEl(self.horisons.ephemeris_file_path)
        
        return self.compute_pointing_loop()

    # Compute pointing loop delta time in seconds
    # TODO: also compute the az and el motor pointing speed
    def compute_pointing_loop(self):
        az_daily_rate = self.az_el.get_daily_azimuth_rate() # degrees per second
        el_daily_rate = self.az_el.get_daily_elevation_rate() # degrees per second
        daily_rate = max(az_daily_rate, el_daily_rate) # degrees per second

        # Compute pointing loop delta time in seconds
        # first, make sure the loop delta time is sufficient for motor to move at least the resolution
        loop_delta_time = self.motor_az.MOTOR_ANGLE_RESOLUTION / daily_rate # seconds
        # limit max pointing loop delta time to 30 minutes
        loop_dt_max = 30 * 60 # seconds
        # limit min pointing loop delta time to 0.1 second
        loop_dt_min = 0.1 # seconds
        loop_delta_time = min(max(loop_delta_time, loop_dt_min), loop_dt_max)
        print("Pointing loop delta time is {} seconds".format(loop_delta_time))

        return loop_delta_time


    # move motors to point to current target
    def point_to_target(self, target_azimuth, target_elevation, az_speed, el_speed):
        status = self.motor_az.move_angle_speed(target_azimuth, az_speed)
        if not status:
            print("ERROR: Failed to move azimuth motor to target position")
            return False
        status = self.motor_el.move_angle_speed(target_elevation, el_speed)
        if not status:
            print("ERROR: Failed to move elevation motor to target position")
            return False
        return True

    def shutdown(self):
        self.motor_az.turn_off_motor()
        self.motor_el.turn_off_motor()
        self.bmm150.set_operation_mode(self.bmm150.POWERMODE_SUSPEND)
        print("Pointing system shutdown.")
        return True
        



