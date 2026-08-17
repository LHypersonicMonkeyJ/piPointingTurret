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
            'sun': '10',
            'moon': '301',
            'iss': '-125544',
            'mercury': '199',
            'venus': '299',
            'earth': '399',
            'mars': '499'
        }
        self.params_dict = {
            'Apparent AZ & EL': '4', # 4 = Apparent Az & El
            'Rates': '5', # 5 = rates (dAZ*cosE, dELV/dt) in arcsec/min
        }
        self.flag_create_file = False
        self.horizons_url = ('https://ssd.jpl.nasa.gov/api/horizons.api')
        self.ephemeris_file_path = None
        self.ephemeris_file_set = set() # a set to keep track of existing ephemeris files

        #define Positions and Time
        self.Earth_id = '399'
        current_location = myutils.get_ip_location()

        self.default_longitude = -95.07639  # Set your default longitude
        self.default_latitude = 29.55889    # Set your default latitude
        self.default_altitude = 9.00000     # Set your default altitude in meters

        # Fallback to default location if API fails
        if current_location is None:
            import warnings
            warnings.warn("Failed to get location from IP; using default coordinates ({}, {}, {})".format(self.default_longitude,
                                                                                                          self.default_latitude,
                                                                                                          self.default_altitude))
            current_location = {
                'longitude': self.default_longitude,  # Set your longitude
                'latitude': self.default_latitude,    # Set your latitude
                'altitude': self.default_altitude,     # Set your altitude in meters
                'utc_offset': '-5'      # Set your UTC offset
            }

        self.longitude = current_location['longitude'] #degrees
        self.latitude = current_location['latitude'] #degrees
        self.altitude = current_location['altitude'] #meters
        self.utc_offset = current_location['utc_offset']
        self.today_date = datetime.today().strftime('%Y-%b-%d')
        self.start_time = f"{self.today_date} UT{self.utc_offset}"
        self.stop_time  = (datetime.today() + timedelta(days=1)).strftime('%Y-%b-%d')
        self.step_size = '5m'

    def reinitialize(self):
        current_location = myutils.get_ip_location()

        # Fallback to default location if API fails
        if current_location is None:
            import warnings
            warnings.warn("Failed to get location from IP; using default coordinates ({}, {}, {})".format(self.default_longitude, 
                                                                                                          self.default_latitude, 
                                                                                                          self.default_altitude))
            current_location = {
                'longitude': self.default_longitude,
                'latitude': self.default_latitude,
                'altitude': self.default_altitude,
                'utc_offset': '-5'
            }

        self.longitude = current_location['longitude']
        self.latitude = current_location['latitude']
        self.altitude = current_location['altitude'] #meters
        self.utc_offset = current_location['utc_offset']
        #self.altitude = 0.0 #meters
        self.utc_offset = current_location['utc_offset']
        self.today_date = datetime.today().strftime('%Y-%b-%d')
        self.start_time = self.today_date + ' UT' + self.utc_offset
        self.stop_time = (datetime.today() + timedelta(days=1)).strftime('%Y-%b-%d')

        self.utc_offset = self.current_location['utc_offset']
        self._update_start_stop()

    # ---------- helper: build params dict for requests ----------
    def _build_params_dict(self, command, step_size):
        return {"format": "json",
                "EPHEM_TYPE": "OBSERVER",
                "OBJ_DATA": "NO",
                "COMMAND": f"'{command}'",
                "START_TIME": f"'{self.start_time}'",
                "STOP_TIME": f"'{self.stop_time}'",
                "STEP_SIZE": f"'{step_size}'",
                "CENTER": f"'coord @ {self.Earth_id}'",
                # Horizons expects site altitude in km
                "SITE_COORD": f"'{self.longitude:.6f},{self.latitude:.6f},{self.altitude*1e-3:.6f}'",
                "QUANTITIES": f"'{self.quantities}'",
        }
    
    # ---------- helper: parse rates from result text ----------
    @staticmethod
    def _parse_rates_arcsec_per_min(result_text):
        """
        Returns max absolute rate in deg/min across both components:
        max(|dAZ|, |dELV|), where dAZ reconstructed from dAZ*cosE and Elev.
        Input is the Horizons 'result' text.
        """
        # Extract rows between $$SOE and $$EOE
        m = re.search(r"\$\$SOE(.*?)\$\$EOE", result_text, re.S)
        if not m:
            return None
        block = m.group(1)

        # Columns in your first ephemeris: time, az, el, dAZ*cosE, d(ELV)/dt
        # Values are whitespace-separated; ‘m’, ‘C’, ‘N’ markers may appear after time.
        max_rate_deg_per_min = 0.0

        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("$$") or line.startswith("Date"):
                continue
            parts = line.split()
            # We expect at least: date, time, (optional marker), az, el, dAZ*cosE, dELVdt
            # Robustly grab the last 4 numeric columns:
            nums = []
            for tok in parts[::-1]:
                try:
                    nums.append(float(tok))
                except ValueError:
                    # skip non-numbers (markers like 'm', 'C', etc.)
                    pass
                if len(nums) >= 4:
                    break
            if len(nums) < 4:
                continue
            # nums collected in reverse: [dELVdt, dAZcosE, EL, AZ] (last 4 numbers)
            dELV_dt_arcsec_min = nums[0]
            dAZcosE_arcsec_min = nums[1]
            el_deg             = nums[2]
            # Reconstruct dAZ = (dAZ*cosE) / cos(E)
            cosE = max(1e-6, abs(__import__('math').cos(__import__('math').radians(el_deg))))
            dAZ_dt_arcsec_min = dAZcosE_arcsec_min / cosE

            # Convert to deg/min
            dAZ_dt_deg_min  = dAZ_dt_arcsec_min  / 3600.0
            dELV_dt_deg_min = dELV_dt_arcsec_min / 3600.0

            rate = max(abs(dAZ_dt_deg_min), abs(dELV_dt_deg_min))
            if rate > max_rate_deg_per_min:
                max_rate_deg_per_min = rate

        return max_rate_deg_per_min if max_rate_deg_per_min > 0 else None
    
    # ---------- compute adaptive step from max rate ----------
    def _choose_step_from_rate(self, max_rate_deg_per_min,
                               target_delta_per_sample_deg=0.2,
                               min_step_s=1, max_step_s=300):
        """
        Pick a STEP_SIZE that keeps per-sample angular change below target_delta_per_sample_deg.
        """
        if not max_rate_deg_per_min or max_rate_deg_per_min <= 0:
            return "60s"  # safe default
        # time = delta / rate
        dt_min = target_delta_per_sample_deg / max_rate_deg_per_min
        dt_s = max(min_step_s, min(max_step_s, int(dt_min * 60)))
        # Express as Horizons step string
        return f"{dt_s}s" if dt_s < 60 else f"{dt_s//60}m"

    # ---------- public: request ephemeris with dynamic step ----------
    def request_ephemeris(self, target_name):
        #get the selected id
        target_key = target_name.lower()
        print("target_key: {}".format(target_key))
        if target_key in self.id_dict:
            selected_id = self.id_dict[target_key]
        else:
            print("Invalid target name: {}".format(target_name))
            return

        #create output file
        today_str = datetime.today().strftime('%Y-%b-%d')
        output_file_name = 'id'+selected_id + '_' + today_str + '.txt'
        self.ephemeris_file_path = os.path.join(os.getcwd(), 'ephemeris', output_file_name)
        if os.path.exists(self.ephemeris_file_path):
            self.ephemeris_file_set.add(self.ephemeris_file_path)
            self.flag_create_file = False
            print("File already exists: {}".format(self.ephemeris_file_path))
            # remote all the files that has the same id but different date
            for file in self.ephemeris_file_set:
                if selected_id in file and file != self.ephemeris_file_path:
                    os.remove(file)
                    print("Deleted file: {}".format(file))
                    self.ephemeris_file_set.remove(file)
        else:
            # remove all the files that has the same id
            for file in self.ephemeris_file_set:
                if selected_id in file:
                    os.remove(file)
                    print("Deleted file: {}".format(file))
                    self.ephemeris_file_set.remove(file)
            self.ephemeris_file_set.add(self.ephemeris_file_path)
            self.flag_create_file = True
            print("Creating file: {}".format(self.ephemeris_file_path))

        # ---------------------------------------------------------
        # Request target position data from Horizons API:
        # target position relative to oberver expressed in ICRF coordinate
        # ---------------------------------------------------------
        print("Requesting ephemeris data for target: {}".format(target_name))
        print("My longitude: {:.5f}".format(self.longitude))
        print("My latitude: {:.5f}".format(self.latitude))
        print("My altitude: {:.5f}".format(self.altitude))

        site_coord = ("{:.8f},{:.8f},{:.8f}".format(self.longitude, self.latitude, self.altitude*1e-3)) #note: altitude is in km
        params = {'format': 'json',
                  'EPHEM_TYPE': 'OBSERVER',
                  'OBJ_DATA': 'NO',
                  'COMMAND': selected_id,
                  'START_TIME': f"'{self.start_time}'",
                  'STOP_TIME': f"'{self.stop_time}'",
                  'STEP_SIZE': f"'{self.step_size}'",
                  'CENTER': 'coord@{}'.format(self.Earth_id),
                  'SITE_COORD': f"'{site_coord}'",
                  'OUT_UNITS': 'KM-S', # km and seconds
                  'REF_SYSTEM': 'ICRF', # ICRF coordinate system
                  # Important: ICRF equatorial plane instead of ecliptic plane, which is the default for Horizons
                  'REF_PLANE': 'FRAME',
                  'CSV_FORMAT': 'YES', # Return data in CSV format
                  'TIME_TYPE': 'UT', # Use UT time
                }

        #request data
        print("[INFO] Requesting data from Horizons API with timeout=30s...")
        print(f"[INFO] Using coordinates: lat={self.latitude}, lon={self.longitude}, alt={self.altitude}m")
        try:
            response = requests.get(self.horizons_url, params=params, timeout=30)
            print("[INFO] Horizons API response received")
        except requests.exceptions.Timeout:
            print("[ERROR] Horizons API timeout after 30 seconds")
            return
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Horizons API request failed: {e}")
            return

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
        else:
            print("Horizons HTTP error: {}".format(response.status_code))
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
    


