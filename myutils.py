import os
import requests
import warnings

def get_ip():
    response = requests.get('https://api.ipify.org?format=json').json()
    return response['ip']

def get_ip_location():
    positionstack_url = f"http://api.positionstack.com/v1/reverse"
    api_key = '0de682ee668f615fd563e07c04a8a933'
    ip_address = get_ip()
    positionstack_url += f"?access_key={api_key}&query={ip_address}"
    positionstack_url += f"&timezone_module=1"

    response = requests.get(positionstack_url)
    #print(response.json())
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data'] is not None:
            response_data = data['data'][0]
            location_data = {
                'city':response_data.get('locality', 'Not Available'),
                'state':response_data.get('region', 'Not Available'),
                'country':response_data.get('country', 'Not Available'),
                'latitude':response_data.get('latitude', 'Not Available'),
                'longitude':response_data.get('longitude', 'Not Available'),
                'utc_offset':response_data.get('timezone_module', 'Not Available').get('offset_string', 'Not Available'),
            }
        else:
            location_data = None
            warnings.warn(f"Error: no data found for ip address {ip_address}")
    else:
        location_data = None
        warnings.warn(f"Error: {response.status_code}")

    return location_data

def get_outdoor_weather(longitude=None, latitude=None):
    # TODO turn this into a class
    # OpenWeatherMap API key
    api_key = '05161901758ed5ab3b8bc0a92eca9f37'
    
    # API endpoint
    api_endpoint = "https://api.openweathermap.org/data/2.5/weather"
    api_endpoint += f"?lat={latitude}&lon={longitude}&appid={api_key}"
    
    # Send the request
    response = requests.get(api_endpoint)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Get the response data
        response_data = response.json()
        
        print(response_data['main'])
        # Get the sea level pressure
        if 'sea_level' in response_data['main']:
            sealevel_pressure = response_data['main']['sea_level']
        else:
            sealevel_pressure = response_data['main']['pressure']
            
        # Get the outdoor temperature
        if 'temp' in response_data['main']:
            outdoor_temp = response_data['main']['temp']
            # Convert from Kelvin to Celsius
            outdoor_temp -= 273.15
            # Convert from Celsisu to Fahrenheit
            outdoor_temp = outdoor_temp * 9 / 5 + 32
        else:
            outdoor_temp = None
            
        # Get the outdoor max temperature
        if 'temp_max' in response_data['main']:
            outdoor_max_temp = response_data['main']['temp_max']
            # Convert from Kelvin to Celsius
            outdoor_max_temp -= 273.15
            # Convert from Celsisu to Fahrenheit
            outdoor_max_temp = outdoor_max_temp * 9 / 5 + 32
        else:
            outdoor_max_temp = None
            
        # Get the outdoor min temperature
        if 'temp_min' in response_data['main']:
            outdoor_min_temp = response_data['main']['temp_min']
            # Convert from Kelvin to Celsius
            outdoor_min_temp -= 273.15
            # Convert from Celsisu to Fahrenheit
            outdoor_min_temp = outdoor_min_temp * 9 / 5 + 32
        else:
            outdoor_min_temp = None
            
        # Get the outdoor humidity
        if 'humidity' in response_data['main']:
            outdoor_humidity = response_data['main']['humidity']
        else:
            outdoor_humidity = None
            
        
        return sealevel_pressure, outdoor_temp, outdoor_max_temp, outdoor_min_temp, outdoor_humidity
    else:
        print(f"Error: {response.status_code}")
        return None

def convert_timezone_delta(delta_str):
    # Parse the input delta string
    delta_hours = int(delta_str[:3])
    
    # Format the result as a string
    result_str = "{:+d}".format(delta_hours)
    
    return result_str

def delete_files_except(folder_path, file_to_keep):
    for file in os.listdir(folder_path):
        if file != file_to_keep:
            os.remove(os.path.join(folder_path, file))

def remove_all_files_in_folder(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        # Iterate through the files and remove them
        for file in files:
            file_path = os.path.join(folder_path, file)

            # Check if it is a file (not a subdirectory)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed: {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def is_steady_state(data, window_size, threshold):
    """
    Check if a measurement has reached its steady state using a moving average.

    Parameters:
    - data: List or numpy array representing the time-series data.
    - window_size: The size of the moving average window.
    - threshold: The threshold for determining steady state.

    Returns:
    - True if the data has reached steady state, False otherwise.
    """
    if len(data) < window_size:
        raise ValueError("Data length should be greater than or equal to the window size.")

    moving_avg = [sum(data[i:i + window_size]) / window_size for i in range(len(data) - window_size + 1)]

    # Check for steady state
    for i in range(len(moving_avg) - 1):
        if abs(moving_avg[i + 1] - moving_avg[i]) > threshold:
            return False

    return True