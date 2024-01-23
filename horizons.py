import sys
import os
import json
import requests
import myutils

from datetime import datetime, timedelta

class Horizons:
    def __init__(self, longtiude=None, latitude=None, altitude=None):
        #initialize variables
        self.id_dict = {
            'Sun': '10',
            'Mercury': '199',
            'Venus': '299',
            'Earth': '399',
            'Mars': '499'
        }
        self.params_dict = {
            'Apparent AZ & EL': '4',
            'Rates': '5',
        }
        self.flag_create_file = False
        self.horizons_url = 'https://ssd.jpl.nasa.gov/api/horizons.api'
        self.ephemeris_file_path = None
        #define Positions and Time
        self.Earth_id = '399'
        current_location = myutils.get_ip_location()
        self.longitude = current_location['longitude'] #degrees
        self.latitude = current_location['latitude'] #degrees
        self.altitude = current_location['altitude'] #meters
        self.utc_offset = current_location['utc_offset']
        self.today_date = datetime.today().strftime('%Y-%b-%d')
        self.start_time = self.today_date + ' UT' + self.utc_offset
        self.stop_time = (datetime.today() + timedelta(days=1)).strftime('%Y-%b-%d')
        self.step_size = '5m'

    def reinitialize(self):
        self.current_location = myutils.get_ip_location()
        self.longitude = self.current_location['longitude']
        self.latitude = self.current_location['latitude']
        self.altitude = self.current_location['altitude'] #meters
        self.utc_offset = self.current_location['utc_offset']
        #self.altitude = 0.0 #meters
        self.utc_offset = self.current_location['utc_offset']
        self.today_date = datetime.today().strftime('%Y-%b-%d')
        self.start_time = self.today_date + ' UT' + self.utc_offset
        self.stop_time = (datetime.today() + timedelta(days=1)).strftime('%Y-%b-%d')

    def request_ephemeris(self, target_name):
        #get the selected id
        target_key = target_name.lower().capitalize()
        if target_key in self.id_dict:
            selected_id = self.id_dict[target_key]
        else:
            print("Invalid target name: {}".format(target_name))
            return

        #create output file
        output_file_name = 'id'+selected_id + '_' + datetime.today().strftime('%Y-%b-%d') + '.txt'
        self.ephemeris_file_path = os.path.join(os.getcwd(), 'ephemeris', output_file_name)
        if os.path.exists(self.ephemeris_file_path):
            myutils.delete_files_except(os.path.join(os.getcwd(), 'ephemeris'), output_file_name)
            self.flag_create_file = False
            print("File already exists: {}".format(self.ephemeris_file_path))
        else:
            #TODO: delete all ephemeris files from a different day
            myutils.remove_all_files_in_folder(os.path.join(os.getcwd(), 'ephemeris'))
            self.flag_create_file = True
            print("Creating file: {}".format(self.ephemeris_file_path))

        #build url commands:
        print("self.longitude: {:.5f}".format(self.longitude))
        print("self.latitude: {:.5f}".format(self.latitude))
        print("self.altitude: {:.5f}".format(self.altitude))
        self.horizons_url += "?format=json&EPHEM_TYPE=OBSERVER&OBJ_DATA=NO"
        self.horizons_url += "&COMMAND='{}'&START_TIME='{}'&STOP_TIME='{}'&STEP_SIZE='{}'".format(selected_id, self.start_time, self.stop_time, self.step_size)
        self.horizons_url += "&CENTER='coord @ {}'&SITE_COORD='{:.5f},{:.5f},{:.5f}'".format(self.Earth_id, self.longitude, self.latitude, self.altitude*1e-3) #note: altitude is in km
        self.horizons_url += "&QUANTITIES='{},{}'".format(self.params_dict['Apparent AZ & EL'], self.params_dict['Rates'])

        #request data
        response = requests.get(self.horizons_url)
        try:
            data = json.loads(response.text)
        except ValueError:
            print("Unable to decode JSON results")
            return
            # sys.exit(1)

        #if the request was valid
        if (response.status_code == 200):
            if 'signature' in data and self.flag_create_file:
                print("Horizons API request signature: {}".format(data['signature']))
                #write data to file
                with open(self.ephemeris_file_path, 'w') as output_file:
                    output_file.write(data['result'])
                print("Ephemeris file created!")

        # If the request was invalid, extract error content and display it:
        if (response.status_code == 400):
          data = json.loads(response.text)
          if "message" in data:
            print("MESSAGE: {}".format(data["message"]))
          else:
            print(json.dumps(data, indent=2))

        # return target ephermeris valid date
        return self.start_time
    
    def get_today_date(self):
        return self.today_date
    
    def get_ephemeris_file_path(self):
        return self.ephemeris_file_path
    
    def get_my_longitude(self):
        longitude_float=float(self.longitude)
        return longitude_float

    def get_my_latitude(self):
        latitude_float=float(self.latitude)
        return latitude_float
    
    def get_my_altitude(self):
        altitude_float=float(self.altitude)
        return altitude_float
    


