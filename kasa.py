
import pip._vendor.requests as requests
from kasa_secrets import DEVICE_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, PROJECT_ID

'''
This program uses the KASA API in order to 
determine if the device connected to the KASA
needs to be turned on or off

'''


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

# Return DEVICE_ID in a json
    @staticmethod
    def get_device_json():
        return  {
            'device_ids': [
                f'{DEVICE_ID}',
            ],
        }

class _KasaConstants:
    ERROR = 'ERROR'
    CONNECTION_ERROR = 'CONNECTION_ERROR'
    START_OF_API_CALL = "https://smartdevicemanagement.googleapis.com/v1/enterprises/"
    SUCCESS = 'SUCCESS'

#Method to authenticate and obtain a token
def getKasaToken(kasaUser, kasaSecret):
    payload = {
            "method": "login",
            "params": {
                "appType": "Kasa_Android",
                "cloudUserName": kasaUser,
                "cloudPassword": kasaSecret,
               "terminalUUID": "5ad873c4-ef16-45aa-88f2-35c4fdd4b563"
            }
    }
    response = requests.post(url="https://wap.tplinkcloud.com/", json=payload)
    obj = response.json()
    token = obj["result"]["token"]
    
    

# generates new token so that a call can be made to the API
def __get_new_token():
    # make a request to get a new token using a refresh token
    params = {
        'client_id': f'{CLIENT_ID}',
        'client_secret': f'{CLIENT_SECRET}',
        'refresh_token': f'{REFRESH_TOKEN}',
        'grant_type': 'refresh_token',
    }
    
    try:
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return _Helper.CONNECTION_ERROR
        
    if 'error' not in response.json():
        _Helper.ACCESS_TOKEN = response.json()['access_token']
    else:
        print("Error retrieving token")
        return _Helper.ERROR
    
    # call is required to complete authentication of new token (just need to make a call using get())
    __get_device_info()


# makes API call to get kasa data for device
def __get_device_info():
    try:
        response = requests.get(f'{_Helper.START_OF_API_CALL}{PROJECT_ID}/devices/{DEVICE_ID}', headers=_Helper.get_headers())
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return _Helper.CONNECTION_ERROR

    if 'error' in response.json():
        print("Connecting to Kasa Device Failed...")
        return _Helper.ERROR

    return response

#obatains device state 
def getKasaDeviceState(token, deviceID, deviceState):
    payload = {
            "method": "passthrough",
            "params": {
                "deviceId": deviceID,
                "requestData":
                    '{\"system\":{\"set_relay_state\":{\"state\":' + str(deviceState) + '}}}'
            }
        }
    response = requests.post(url="https://use1-wap.tplinkcloud.com/?token={}".format(token), json=payload)

#changes the device status to the opposite 
def flip_switch():
    state = getKasaDeviceState
    if state == 1:
        return 0
    elif state == 0:
        return 1