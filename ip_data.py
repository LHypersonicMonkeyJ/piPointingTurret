import os
import sys
import requests
import warnings

# write a class that takes an ip address and a date as input 
# and returns location and weather data
class IP_Data():
    def __init__(self):
        self.ipify_url = 'https://api.ipify.org?format=json'
        self.positionstack_url = f"http://api.positionstack.com/v1/reverse"
        self.positionstack_api_key = '0de682ee668f615fd563e07c04a8a933'
        self.openweathermap_url = "https://api.openweathermap.org/data/2.5/weather"
        self.openweathermap_api_key = '05161901758ed5ab3b8bc0a92eca9f37'
        self.ip_address = self._request_ip()

        # initialize location data from ip address
        self.city = None
        self.state = None
        self.country = None
        self.latitude = None
        self.longitude = None
        self.utc_offset = None
        self._get_position_data(self.ip_address)

    def _request_ip(self):
        response = requests.get(self.ipify_url).json()
        return response['ip']
    
    def _get_position_data(self, ip_address):
        positionstack_url = self.positionstack_url
        positionstack_url += f"?access_key={self.positionstack_api_key}&query={ip_address}"
        positionstack_url += f"&timezone_module=1"
        response = requests.get(positionstack_url)

        # check repsonse status code
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data'] is not None:
                response_data = data['data'][0]
                self.city = response_data.get('locality', 'Not Available')
                self.state = response_data.get('region', 'Not Available')
                self.country = response_data.get('country', 'Not Available')
                self.latitude = response_data.get('latitude', 'Not Available')
                self.longitude = response_data.get('longitude', 'Not Available')
                self.utc_offset = response_data.get('timezone_module', 'Not Available').get('offset_string', 'Not Available')
            else:
                location_data = None
                warnings.warn(f"Error: no data found for ip address {ip_address}")
        else:
            location_data = None
            warnings.warn(f"Error: {response.status_code}")
        
        return True
    
    # Public Methods
    def update_outdoor_weather(self):
        openweathermap_url = self.openweathermap_url
        openweathermap_url += f"?lat={self.latitude}&lon={self.longitude}&appid={self.openweathermap_api_key}"
        response = requests.get(openweathermap_url)

        # check response status code

    # Getters
    def get_city(self):
        return self.city
    
    def get_state(self):
        return self.state
    
    def get_country(self):
        return self.country
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_utc_offset(self):
        return self.utc_offset
    
    def get_ip_address(self):
        return self.ip_address
    



