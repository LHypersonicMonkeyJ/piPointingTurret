import os
import requests

def get_ip():
    response = requests.get('https://api.ipify.org?format=json').json()
    return response['ip']

def get_location():
    ip_address = get_ip()
    response = requests.get(f'http://ipapi.co/{ip_address}/json/').json()
    location_data = {
        'city': response['city'],
        'region': response['region'],
        'country': response['country_name'],
        'latitude': response['latitude'],
        'longitude': response['longitude'],
        'utc_offset': response['utc_offset'],
    }
    return location_data

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