import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from pointing import pointing

p1 = pointing()

indoor_temp = p1.get_indoor_temperature()

print("today's date: {}".format(p1.get_today_date()))