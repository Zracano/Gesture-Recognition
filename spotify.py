from datetime import datetime, timedelta
import time
from spotify_secrets import DEVICE_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
import requests

# Methods (available to use):
# RETURN VALUES
# returns {ERROR or CONNECTION_ERROR} dependong on error
# nothing if successful

# starts/resumes the playback
# start_playback()

# pauses the playback
# pause_playback()

# skips to the next song and plays it
# skip_playback()

# goes back to a previous song and plays it
# previous_playback()

class _Helper:
    # Token info storage
    access_token = None
    token_expiration = None

    # Return header info for API calls
    def get_headers():
        return {
            'Authorization': f"Bearer {_Helper.access_token}"
        }

class _SpotifyConstants:
    # URL endpoint for API calls
    TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
    DEVICES_ENDPOINT = "https://api.spotify.com/v1/me/player/devices"
    START_PLAYBACK_ENDPOINT = f"https://api.spotify.com/v1/me/player/play?{DEVICE_ID}"
    PAUSE_PLAYBACK_ENDPOINT = f"https://api.spotify.com/v1/me/player/pause?{DEVICE_ID}"
    SKIP_TO_NEXT_ENDPOINT = f"https://api.spotify.com/v1/me/player/next?{DEVICE_ID}"
    SKIP_TO_PREVIOUS_ENDPOINT = f"https://api.spotify.com/v1/me/player/previous?{DEVICE_ID}"

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
    #payload = f'grant_type=refresh_token&refresh_token={REFRESH_TOKEN}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}'
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
    
    # Make API call
    try:
        response = requests.put(_SpotifyConstants.START_PLAYBACK_ENDPOINT, headers=headers, data={})
    except:
        return _SpotifyConstants.CONNECTION_ERROR
    
    # Check API response
    if (response.status_code == 201):
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
    if (response.status_code == 201):
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
    if (response.status_code == 201):
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
    if (response.status_code == 201):
        return _SpotifyConstants.SUCCESS
    else:
        return _SpotifyConstants.ERROR

# Start Playback (public)
def start_playback():
    __start_playback()

# Pause Playback (public)
def pause_playback():
    __pause_playback()

# Skip Playback (public)
def skip_playback():
    __skip_playback()

# Previous Playbak (public)
def previous_playback():
    __previous_playback()

def main():
    # for testing purposes
    start_playback()
    time.sleep(5)
    skip_playback()
    time.sleep(5)
    previous_playback()
    time.sleep(5)
    pause_playback()
    
if __name__ == '__main__':
    main()