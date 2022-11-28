from datetime import datetime, timedelta
from spotify_secrets_private import DEVICE_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
import requests

# Methods (available to use):
# RETURN VALUES
# returns {ERROR or CONNECTION_ERROR} depending on error
# returns SUCCESS otherwise

# starts/resumes the playback
# start_playback()

# pauses the playback
# pause_playback()

# skips to the next song and plays it
# skip_playback()

# goes back to a previous song and plays it
# previous_playback()

# return playing status of device
# is_playing()

# Change playback volume 
# paramter: increment - signed int {change volume by the increment value}
# change_volume(increment):

class _Helper:
    # Token info storage
    access_token = None
    token_expiration = None

    # Return header info for API calls
    @staticmethod
    def get_headers():
        return {
            'Authorization': f"Bearer {_Helper.access_token}"
        }
    
    # Return header info for Volume calls   
    @staticmethod
    def get_volume_header():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {_Helper.access_token}",
        }
        
     # Return DEVICE_ID in a json
    @staticmethod
    def get_device_json():
        return  {
            'device_ids': [
                f'{DEVICE_ID}',
            ],
        }
        
    # Return DEVICE_ID in a json
    @staticmethod
    def set_volume_json(new_vol):
        return  {
            'volume_percent' : f"{new_vol}",
            'device_id' : f'{DEVICE_ID}',
        }
        
class _SpotifyConstants:
    # URL endpoint for API calls
    TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
    DEFAULT_URL = "https://api.spotify.com/v1/me/player"
    DEVICES_ENDPOINT = f"{DEFAULT_URL}/devices"
    START_PLAYBACK_ENDPOINT = f"{DEFAULT_URL}/play?{DEVICE_ID}"
    PAUSE_PLAYBACK_ENDPOINT = f"{DEFAULT_URL}/pause?{DEVICE_ID}"
    SKIP_TO_NEXT_ENDPOINT = f"{DEFAULT_URL}/next?{DEVICE_ID}"
    SKIP_TO_PREVIOUS_ENDPOINT = f"{DEFAULT_URL}/previous?{DEVICE_ID}"
    VOLUME_ENDPOINT = f"{DEFAULT_URL}/volume?{DEVICE_ID}"

    # Standard return values
    # For status codes other than 200 and 201
    ERROR = 'ERROR' 
    CONNECTION_ERROR = 'CONNECTION_ERROR'
    SUCCESS = 'SUCCESS'

# Refresh Token
def __refresh_token(bypass_check=False):
    # Check if refresh is necessary
    if (_Helper.token_expiration and not bypass_check):
        # If current time is still under expiration time, no need to refresh token
        if (datetime.now() < _Helper.token_expiration):
            return _SpotifyConstants.SUCCESS
    # Otherwise, refresh token
    # Generate aspects of API call
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': f'{REFRESH_TOKEN}',
        'client_id': f'{CLIENT_ID}',
        'client_secret': f'{CLIENT_SECRET}'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Make API call
    try:
        response = requests.post(_SpotifyConstants.TOKEN_ENDPOINT, headers=headers, data=payload)
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if response and response.status_code == 200:
        json_data = response.json()
        if (json_data and 'access_token' in json_data and 'expires_in' in json_data):
            _Helper.access_token = json_data['access_token']
            _Helper.token_expiration = datetime.now() + timedelta(seconds = int(json_data['expires_in'])-10)
            return _SpotifyConstants.SUCCESS
        else:
            return _SpotifyConstants.ERROR
    else:
        None

# Start Playback (private)
def __start_playback():
    # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # set device to be active if it is not via API call
    set_active_device = __get_device_info()
    if set_active_device:
        error_status = __set_active_device()
        if error_status in [_SpotifyConstants.ERROR, _SpotifyConstants.CONNECTION_ERROR]:
            return error_status
    
    # Make API call
    try:
        response = requests.put(_SpotifyConstants.START_PLAYBACK_ENDPOINT, headers=headers, data={})
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if (response.status_code == 202):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# Pause Playback (private)
def __pause_playback():
    # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.put(_SpotifyConstants.PAUSE_PLAYBACK_ENDPOINT , headers=headers, data={})
    except:
        return _SpotifyConstants.CONNECTION_ERROR
 
    # Check API response
    if (response.status_code == 202):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# Skip Playback (private)
def __skip_playback():
    # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.post(_SpotifyConstants.SKIP_TO_NEXT_ENDPOINT, headers=headers, data={})
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if (response.status_code == 202):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# Previous Playback (private)
def __previous_playback():
    # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.post(_SpotifyConstants.SKIP_TO_PREVIOUS_ENDPOINT, headers=headers, data={})
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if (response.status_code == 202):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR
    
# return playing status of device
def __is_playing():
     # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.get(f'{_SpotifyConstants.DEFAULT_URL}', headers=headers)
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    if (response.status_code == 200):   
        return response.json()['is_playing']
    else:
        return _SpotifyConstants.ERROR
    
# return status of something is_playing 
def __change_volume(change_volume_by):
     # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    _ , current_volume = __get_device_info()
    current_volume += change_volume_by
    
    # Make API call
    try:
        response = requests.put(f'{_SpotifyConstants.VOLUME_ENDPOINT}', headers=headers, params=_Helper.set_volume_json(current_volume))
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    if (response.status_code == 204):   
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# returns "is_active" state and "volume_percent" of raspberry pi device (private)
def __get_device_info():
     # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.get(f'{_SpotifyConstants.DEVICES_ENDPOINT}', headers=headers)
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    transfer_playback = False
    if (response.status_code == 200): 
        for device in response.json()['devices']:
            # raspberry pi found
            if device['id'] == DEVICE_ID:
                if not device['is_active']:
                    transfer_playback = True
                break
            
        return transfer_playback, device['volume_percent']
    else:
        return _SpotifyConstants.ERROR
    
# sets the raspberry pi to be the active device (private)
def __set_active_device():
     # Check token
    __refresh_token()

    # Generate aspects of API call
    headers = _Helper.get_headers()
    
    # Make API call
    try:
        response = requests.put(_SpotifyConstants.DEFAULT_URL, headers=headers, json=_Helper.get_device_json())
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if (response.status_code == 202):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# Start Playback (public)
def start_playback():
    return __start_playback()

# Pause Playback (public)
def pause_playback():
    return __pause_playback()

# Skip Playback (public)
def skip_playback():
    return __skip_playback()

# Previous Playback (public)
def previous_playback():
    return __previous_playback()

# See if something is playing (public)   
def is_playing():
    return __is_playing()

# Change playback volume by a certain increment (public)   
def change_volume(change_volume_by):
    return __change_volume(change_volume_by)
