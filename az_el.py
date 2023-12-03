import re
from datetime import datetime, timedelta

#Define a data structure to store azimuth and elevation
class AzEl:
    def __init__(self, ephemeris_file_path):
        self.data = []
        self.current_azimuth = 0
        self.current_elevation = 0
        self.current_azimuth_rate = 0
        self.current_elevation_rate = 0
        self.parse_ephemeris_data(ephemeris_file_path)
        self.get_az_el(datetime.now())

    def parse_ephemeris_data(self, ephemeris_file_path):
        #open ephemeris file and read all lines
        try:
            with open(ephemeris_file_path, 'r') as ephemeris_file:
                lines = ephemeris_file.readlines()
                
                #find the index of the line starting with '$$SOE'
                start_index = lines.index('$$SOE\n') + 1
                
                #find the index of the line starting with '$$EOE'
                end_index = lines.index('$$EOE\n')
                
                #define a regualr expression pattern for the line format
                pattern = re.compile(r'(\d{4}-[a-zA-Z]+-\d{2} \d{2}:\d{2})\s+\S+\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+')
                
                #iterate through lines and parse data
                for line in lines[start_index:end_index]:
                    #use regular expression to extract datetime, azimuth, and elevation
                    match = pattern.search(line)

                    if match:
                        date_str, zimuth_str, elevation_str = match.groups()

                        # Parse datetime
                        dt_object = datetime.strptime(date_str, '%Y-%b-%d %H:%M')
                        
                        #store the data in the data structure
                        try:
                            self.data.append({
                                'datetime': dt_object,
                                'azimuth': float(zimuth_str),
                                'elevation': float(elevation_str)
                            })
                        except ValueError:
                            print("Unable to parse line: {}".format(line))
                    else:
                        print("Unable to parse line: {}".format(line))
                        
        except FileNotFoundError:
            print("File not found: {}".format(ephemeris_file_path))
            return

    def linear_interpolate(self, datetime):
        #iterate through the data structure
        for i in range(len(self.data)):
            #check if the current datetime is between the current and next data points
            if self.data[i]['datetime'] <= datetime and self.data[i+1]['datetime'] >= datetime:
                #calculate the time difference between the current and next data points
                delta_time = self.data[i+1]['datetime'] - self.data[i]['datetime']
                #calculate the time difference between the current datetime and the current data point
                delta_time_current = datetime - self.data[i]['datetime']
                #calculate the time difference between the current datetime and the next data point
                delta_time_next = self.data[i+1]['datetime'] - datetime
                #calculate the weight of the current data point
                weight_current = delta_time_next / delta_time
                #calculate the weight of the next data point
                weight_next = delta_time_current / delta_time
                #calculate the interpolated azimuth
                azimuth = self.data[i]['azimuth'] * weight_current + self.data[i+1]['azimuth'] * weight_next
                #calculate the interpolated elevation
                elevation = self.data[i]['elevation'] * weight_current + self.data[i+1]['elevation'] * weight_next
                #return the interpolated azimuth and elevation
                return azimuth, elevation
    
    def find_nearest_index(self, datetime):
        #iterate through the data structure
        for i in range(len(self.data)):
            #check if the current datetime is between the current and next data points
            if self.data[i]['datetime'] <= datetime and self.data[i+1]['datetime'] >= datetime:
                #return the index of the current data point
                return i
            
    def get_az_el(self, datetime):
        #check if the datetime is within the range of the ephemeris data
        if datetime < self.data[0]['datetime'] or datetime > self.data[-1]['datetime']:
            print("Datetime is outside the range of the ephemeris data")
            return None
        #check if the datetime is the same as the current datetime
        elif datetime == self.data[0]['datetime']:
            self.current_azimuth = self.data[0]['azimuth']
            self.current_elevation = self.data[0]['elevation']
            time_delta = self.data[1]['datetime'] - self.data[0]['datetime']
            minutes = time_delta.total_seconds() / 60
            minutes_as_float = float(minutes)
            self.current_azimuth_rate = (self.data[1]['azimuth'] - self.data[0]['azimuth'])/minutes_as_float
            self.current_elevation_rate = (self.data[1]['elevation'] - self.data[0]['elevation'])/minutes_as_float
        #check if the datetime is the same as the next datetime
        elif datetime == self.data[-1]['datetime']:
            self.current_azimuth = self.data[-1]['azimuth']
            self.current_elevation = self.data[-1]['elevation']
            time_delta = self.data[-1]['datetime'] - self.data[-2]['datetime']
            minutes = time_delta.total_seconds() / 60
            minutes_as_float = float(minutes)
            self.current_azimuth_rate = (self.data[-1]['azimuth'] - self.data[-2]['azimuth'])/minutes_as_float
            self.current_elevation_rate = (self.data[-1]['elevation'] - self.data[-2]['elevation'])/minutes_as_float
        #check if the datetime is between the current and next datetime
        elif datetime > self.data[0]['datetime'] and datetime < self.data[-1]['datetime']:
            self.current_azimuth, self.current_elevation = self.linear_interpolate(datetime)
            i = self.find_nearest_index(datetime)
            time_delta = self.data[i+1]['datetime'] - self.data[i]['datetime']
            minutes = time_delta.total_seconds() / 60
            minutes_as_float = float(minutes)
            self.current_azimuth_rate = (self.data[i+1]['azimuth'] - self.data[i]['azimuth'])/minutes_as_float
            self.current_elevation_rate = (self.data[i+1]['elevation'] - self.data[i]['elevation'])/minutes_as_float
        else:
            print("Unable to calculate azimuth and elevation")
        

    def get_current_azimuth(self):
        return self.current_azimuth
    
    def get_current_elevation(self):
        return self.current_elevation
    
    def get_current_azimuth_rate(self):
        return self.current_azimuth_rate
    
    def get_current_elevation_rate(self):    
        return self.current_elevation_rate