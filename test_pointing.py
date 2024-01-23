# test the pointing class
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from pointing import pointing

pointing = pointing()

# get today's outdoor weather
max_outdorr_temp = pointing.outdoor_max_temp
min_outdorr_temp = pointing.outdoor_min_temp

# get current outdoor weather
pointing.update_outdoor_weather()
current_outdoor_temp = pointing.outdoor_temp
current_outdoor_feellike_temp = pointing.outdoor_feellike_temp
current_outdoor_humidity = pointing.outdoor_humidity
current_outdoor_pressure = pointing.outdoor_sealevel_pressure

# get current indoor weather
current_indoor_temp = pointing.get_indoor_temperature()
current_indoor_humidity = pointing.get_indoor_humidity()
current_indoor_pressure = pointing.get_indoor_pressure()


# print to console
print("Today's outdoor max temperature: {:.2f} deg F".format(max_outdorr_temp))
print("Today's outdoor min temperature: {:.2f} deg F".format(min_outdorr_temp))

print("Current outdoor temperature: {:.2f} deg F".format(current_outdoor_temp))
print("Current outdoor humidity: {:.2f} %".format(current_outdoor_humidity))
print("Current outdoor pressure: {:.2f} hpa".format(current_outdoor_pressure))

print("Current indoor temperature: {:.2f} deg F".format(current_indoor_temp))
print("Current indoor humidity: {:.2f} %".format(current_indoor_humidity))
print("Current indoor pressure: {:.2f} hpa".format(current_indoor_pressure))