# importing this because [#import requests] does not work on vscode
import pip._vendor.requests as requests
from secrets import PROJECT_ID, DEVICE_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

'''
Methods (available to use):
# RETURN VALUES
# returns {Helper.ERROR or Helper.CONNECTION_ERROR} depending on error
# nothing if successful

# get current mode of Nest Thermostat (COOL, HEAT, OFF)
get_current_temp_mode()

# get current temp (if mode is OFF, a 0 is returned)
get_current_temp()

# value (int{set temperate [number]}, or string{set mode ["OFF", "HOT", "COOL"]})
# command (string{"SetCool", "SetHeat", "SetMode"})
# info: "SetCool", "SetHeat" used with setting temperate number
# info: "OFF", "HOT", "COOL" used with "SetMode"
update_thermostat(value, command)
'''

class Helper:
    # every time program runs or hourly, the access token changes
    ACCESS_TOKEN = None
    ERROR = 'ERROR'
    CONNECTION_ERROR = 'CONNECTION_ERROR'
    # constants
    COOL, HEAT, OFF, MODE = "COOL", "HEAT", "OFF", "mode"
    CELSIUS = "CELSIUS"
    COOL_COMMAND, HEAT_COMMAND, CHANGE_MODE_COMMAND = "SetCool", "SetHeat", "SetMode"
    HEAT_FIELD, COOL_FIELD = "heatCelsius", "coolCelsius"
    # useful methods for converting temperates
    from_c_to_fahrenheit = lambda celsius : round((celsius * 1.8) + 32, 1) 
    from_f_to_celsuis = lambda fahrenheit : round((fahrenheit - 32) / 1.8, 1)
    
    # headers for API Calls
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Helper.ACCESS_TOKEN}',
        }
    
    # params for API Calls
    def get_params(value, command):
        param = ""
        command_mode = "ThermostatTemperatureSetpoint" if command in {Helper.COOL_COMMAND, Helper.HEAT_COMMAND} \
            else "ThermostatMode"
        if command == Helper.HEAT_COMMAND:
            param, value = Helper.HEAT_FIELD, Helper.from_f_to_celsuis(value)
        elif command == Helper.COOL_COMMAND:
            param, value = Helper.COOL_FIELD, Helper.from_f_to_celsuis(value)
        else:
            param = Helper.MODE
        return  {
            'command': f'sdm.devices.commands.{command_mode}.{command}',
            'params': {
                param: value,
            },
        }

class __Nest_Thermostat:
    def __init__(self, response):
        self.temperature_scale = response.json()["traits"]["sdm.devices.traits.Settings"]["temperatureScale"]
        self.device_mode = response.json()["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
        # json returns either one of these values or none, but never both at the same time (for current use-case)
        try:
            self.device_heat_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["heatCelsius"]))
        except KeyError:
            self.device_heat_temp = 0
        try:
            self.device_cool_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["coolCelsius"]))
        except KeyError:
            self.device_cool_temp = 0

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
        return Helper.CONNECTION_ERROR
        
    if 'error' not in response.json():
        Helper.ACCESS_TOKEN = response.json()['access_token']
    else:
        print("Error retrieving token")
        return Helper.ERROR
    
    # call is required to complete authentication of new token (just need to call using get() to accomplish)
    __get_device_info();

def __get_device_info():
    try:
        response = requests.get(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}', headers=Helper.get_headers())
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return Helper.CONNECTION_ERROR
    
    if 'error' in response.json():
        print("Connecting to Nest Device Failed...")
        return Helper.ERROR

    return response

def __is_thermostat_off():
    nest_device = __get_nest_data()
    return False if nest_device in {Helper.ERROR, Helper.CONNECTION_ERROR} or nest_device.device_mode != Helper.OFF else True
    
def __update_thermostat(value, command, internal_method):
    # if thermostat is off, change mode to either COOL or HEAT (API requirement)
    if command in {Helper.COOL_COMMAND, Helper.HEAT_COMMAND} and __is_thermostat_off():
        set_mode = Helper.COOL if command == Helper.COOL_COMMAND else Helper.HEAT
        status = __update_thermostat(set_mode, Helper.CHANGE_MODE_COMMAND, True)
        if status == Helper.ERROR:
            print("Updating thermostat failed, cannot change mode due to API connection error")
            return Helper.ERROR
    
    try:
        response = requests.post(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}:executeCommand', headers=Helper.get_headers(), json=Helper.get_params(value, command))
    except (requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
        return Helper.CONNECTION_ERROR
    
    if 'error' not in response.json():
        print(f"Thermostat: (command - {command} , value: - {value})")
    else:
        print(f"Error changing thermostat to {command} and {value}")
        return Helper.ERROR

def update_thermostat(value, command):
    __get_new_token()
    return __update_thermostat(value, command, True)

# establish connection to NEST Api and return object with desired data    
def __get_nest_data():
    # re-new authentication
    __get_new_token()
    # get NEST data from API
    nest_data = __get_device_info()
    try:
        # create object with only data wanted
        nest_device = __Nest_Thermostat(nest_data)
    except AttributeError:
        return nest_data
    
    return nest_device
   
# get current temp of thermostat    
def get_current_temp():
    nest_device = __get_nest_data()
    if nest_device not in {Helper.ERROR, Helper.CONNECTION_ERROR}:
        temp = nest_device.device_cool_temp if nest_device.device_mode == Helper.COOL \
            else nest_device.device_heat_temp if nest_device.device_mode == Helper.HEAT \
            else 0
        return temp, nest_device.device_mode if temp is not None else "OFF"
    else:
        return nest_device
    
# get current temp of thermostat    
def get_current_temp_mode():
    nest_device = __get_nest_data()
    if nest_device not in {Helper.ERROR, Helper.CONNECTION_ERROR}:
        return nest_device.device_mode
    else:
        return nest_device