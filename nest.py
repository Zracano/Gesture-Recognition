# import requests (might need to use this import on raspberry pi)
from socket import herror
import pip._vendor.requests as requests # using this because import requests does not work on vscode
from secrets import PROJECT_ID, DEVICE_ID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

# GESTURE
# rotate your index finger in a circle clockwise to go up and counter-clockwise to turn off
# to change thermometer mode between HEAT, COOL, OFF, make an initial gesture, after 
# that, they just choose 1, 2, 3 (speaker will call out options along with their associated gesture)

class Helper:
    # every time program runs or hourly, the access token changes
    ACCESS_TOKEN = None
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
        command_mode = "ThermostatTemperatureSetpoint" if command in {Helper.COOL_COMMAND, Helper.HEAT_COMMAND} \
            else "ThermostatMode"
        param = ""
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

class Nest_Thermostat:
    def __init__(self, response):
        self.temperature_scale = response.json()["traits"]["sdm.devices.traits.Settings"]["temperatureScale"]
        self.device_mode = response.json()["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
        # json returns either one of these values or none, but never both at the same time for our use-cases
        try:
            self.device_heat_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["heatCelsius"]))
        except KeyError:
            self.device_heat_temp = 0
        try:
            self.device_cool_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["coolCelsius"]))
        except KeyError:
            self.device_cool_temp = 0
    
    # return the command based on current device mode        
    get_command = lambda self : Helper.COOL_COMMAND if self.device_mode == Helper.COOL \
        else Helper.HEAT_COMMAND if self.device_mode == Helper.HEAT \
        else Helper.CHANGE_MODE_COMMAND

def get_new_token():
    # make a request to get a new token using a refresh token
    response = requests.post(f'https://www.googleapis.com/oauth2/v4/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}&grant_type=refresh_token')
    if 'error' not in response.json():
        Helper.ACCESS_TOKEN = response.json()['access_token']
    else:
        print("Error getting token")
        return
    
    # call is required to complete authentication of new token (just need to call using get() to accomplish)
    get_device_info();

def get_device_info():
    response = requests.get(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}', headers=Helper.get_headers())
    if 'error' in response.json():
        print("Issue connecting to Nest Device")
        return
    
    return response

def is_thermostat_off():
    nest_device = Nest_Thermostat(get_device_info())
    return True if nest_device.device_mode == Helper.OFF else False
    
def update_thermostat(value, command):
    if command in {Helper.COOL_COMMAND, Helper.HEAT_COMMAND} and is_thermostat_off():
        set_mode = Helper.COOL if command == Helper.COOL_COMMAND else Helper.HEAT
        print(f"$$$ Information - {Helper.get_params(set_mode, Helper.CHANGE_MODE_COMMAND)}")
        update_thermostat(set_mode, Helper.CHANGE_MODE_COMMAND)
    
    print(f"$$$ Information - {Helper.get_params(value, command)}")
    
    response = requests.post(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}:executeCommand', headers=Helper.get_headers(), json=Helper.get_params(value, command))
    if 'error' not in response.json():
        print(f"Thermostat set to {value} and {command}")
    else:
        print(f"Error changing thermostat to {value} and {command}")
        print(response.json())
        return

def run_testing():
    # set-up authentication
    get_new_token()
    # get NEST data from API
    # nest_data = get_device_info()
    # create object with the needed NEST data
    # nest_device = Nest_Thermostat(nest_data)
    # update thermostat temp or change temp modes (Heat, Cool, Off)
    update_thermostat(80, "SetCool")
    print("Program terminated.")

# basically acts like main() for testing purposes, will be deleted when testing is done
run_testing()