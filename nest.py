# import requests (might need to use this import on raspberry pi)
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
    
    def get_headers():
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Helper.ACCESS_TOKEN}',
        }
    
    def get_params(value, command):
        param = ""
        if command == Helper.HEAT_COMMAND:
            param, value = Helper.HEAT_FIELD, Helper.from_f_to_celsuis(value)
        elif command == Helper.COOL_COMMAND:
            param, value = Helper.COOL_FIELD, Helper.from_f_to_celsuis(value)
        else:
            param = Helper.MODE, 
        return  {
                'command': f'sdm.devices.commands.ThermostatMode.{command}',
                'params': {
                    param: value,
            },
    }

class Nest_Thermostat:
    def __init__(self, response):
        self.temperature_scale = response.json()["traits"]["sdm.devices.traits.Settings"]["temperatureScale"]
        self.device_mode = response.json()["traits"]["sdm.devices.traits.ThermostatMode"]["mode"]
        # json returns either one of these, but never both at the same time
        try:
            self.device_heat_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["heatCelsius"]))
        except KeyError:
            self.device_heat_temp = 0
        try:
            self.device_cool_temp = Helper.from_c_to_fahrenheit(float(response.json()["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["coolCelsius"]))
        except KeyError:
            self.device_cool_temp = 0
            
    get_command = lambda self : Helper.COOL_COMMAND if self.device_mode == Helper.COOL \
        else Helper.HEAT_COMMAND if self.device_mode == Helper.HEAT \
        else Helper.CHANGE_MODE_COMMAND
        
    def set_temp(self, temp):
        if(self.temperature_scale == Helper.CELSIUS):
            self.device_temp = Helper.from_c_to_fahrenheit(temp)
        else:
            self.device_temp = temp;

    # for testing purposes only, [TO DO - DELETE]
    def show_data(self):
        print(f"Mode: {self.device_mode}, Scale: {self.temperature_scale}, Heat set: {self.device_heat_temp}, Cool set: {self.device_cool_temp}")

def get_new_token():
    # make a request to get a new token using a refresh token
    response = requests.post(f'https://www.googleapis.com/oauth2/v4/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}&grant_type=refresh_token')

    if 'error' not in response.json():
        Helper.ACCESS_TOKEN = response.json()['access_token']
    else:
        print("Error getting token")
        return
    
    # call is required for complete authentication
    response = requests.get(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices', headers=Helper.get_headers())
    
    if 'error' not in response.json():
        print("Authenticating token successful")
    else:
        print("Error making a call to authenticate token")
        return

def get_device_info():
    response = requests.get(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}', headers=Helper.get_headers())

    if 'error' not in response.json():
        if DEVICE_ID in response.json()['name']:
            print("Nest Device Online...retrieving data")
            device = Nest_Thermostat(response)
            device.show_data()
    else:
        print("Issue connecting to Nest Device")
        return
    
    return response

    
def update_thermostat(value, command):
    
    print(f"Information : {Helper.get_params(value, command)}")
    
    response = requests.post(f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{PROJECT_ID}/devices/{DEVICE_ID}:executeCommand', headers=Helper.get_headers(), json=json_data)
    
    if 'error' not in response.json():
        print(f"Thermostat set to {value} and {command}")
    else:
        print(f"Error changing thermostat to {value} and {command}")
        return

# set-up authentication
get_new_token()
nest_data = get_device_info()
# get NEST Device data 
nest_device = Nest_Thermostat(nest_data)
#update_thermostat("HEAT", "SetMode")
print(nest_device.get_command())
print("Program terminated.")