import uuid
import requests
from kasa_secrets import LOGIN_EMAIL, LOGIN_PASSWORD, KASA_SMART_PLUG_NAME

'''
This program controls a Kasa SmartPlug using KASA API
in order to turn it ON and OFF. 
'''

class Kasa:
    ERROR = "ERROR"

# get token to use 
def __get_kasa_token():
    payload = {
            "method": "login",
            "params": {
                "appType": "Kasa_Android",
                "cloudUserName": LOGIN_EMAIL,
                "cloudPassword": LOGIN_PASSWORD,
                "terminalUUID": str(uuid.uuid4())
            }
    }
    
    response = requests.post(url="https://wap.tplinkcloud.com/", json=payload)
    
    # make sure there was not an error
    if response.status_code == 200:
        try: 
            return response.json()["result"]["token"]
        except KeyError:
            return Kasa.ERROR
    else:
        return Kasa.ERROR

# get the status and device id of SmartPlug
def __get_kasa_device_status(token):
    payload = {"method": "getDeviceList"}
    device_list = requests.post(f"https://wap.tplinkcloud.com?token={token}", json=payload)
    
    # find the device based on device name
    for index in range(len(device_list.json())):
        device = device_list.json()['result']['deviceList'][index]
        if device['alias'] == KASA_SMART_PLUG_NAME:
            return device['deviceId']
    
    return Kasa.ERROR

# switch state of plug to whatever the user specfies
def __flip_switch(token, deviceID, deviceState):
    payload = {
            "method": "passthrough",
            "params": {
                "deviceId": deviceID,
                "requestData":
                    '{\"system\":{\"set_relay_state\":{\"state\":' + str(deviceState) + '}}}'
            }
        }
    
    response = requests.post(url=f"https://use1-wap.tplinkcloud.com/?token={token}", json=payload)
    
    if response.status_code != 200:
        return Kasa.ERROR
  
# change the current state of the switch  
def flip_switch(new_state):
    token = __get_kasa_token()
    deviceID = __get_kasa_device_status(token)
    __flip_switch(token, deviceID, new_state)