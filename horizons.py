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
        current_location = myutils.get_location()
        self.longitude = current_location['longitude'] #degrees
        self.latitude = current_location['latitude'] #degrees
        self.altitude = '0' #km
        self.utc_offset = current_location['utc_offset']
        self.start_time = datetime.today().strftime('%Y-%b-%d') + ' UT' + myutils.convert_timezone_delta(self.utc_offset)
        self.stop_time = (datetime.today() + timedelta(days=1)).strftime('%Y-%b-%d')
        self.step_size = '5m'

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
            myutils.remove_all_files_in_folder(os.path.join(os.getcwd(), 'ephemeris'))
            self.flag_create_file = True
            print("Creating file: {}".format(self.ephemeris_file_path))

        #build url commands:
        self.horizons_url += "?format=json&EPHEM_TYPE=OBSERVER&OBJ_DATA=NO"
        self.horizons_url += "&COMMAND='{}'&START_TIME='{}'&STOP_TIME='{}'&STEP_SIZE='{}'".format(selected_id, self.start_time, self.stop_time, self.step_size)
        self.horizons_url += "&CENTER='coord @ {}'&SITE_COORD='{},{},{}'".format(self.Earth_id, self.longitude, self.latitude, self.altitude)
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

        return
    
    def get_ephemeris_file_path(self):
        return self.ephemeris_file_path
    
    def get_my_location(self):
        return {
            'longitude': self.longitude,
            'latitude': self.latitude,
            'altitude': self.altitude
        }

