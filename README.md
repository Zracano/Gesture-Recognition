# Gesture Recognition
1. [APIs](#apis)
    1. [Nest](#nest-api)
    2. [Spotify](#spotify-api)
    3. [Kasa](#kasa-api)
2. [Using Git](#git)
3. [Using Conda](#creating-an-environment)
4. [How to Use](#how-to-use)

## APIs

#### Nest API
###### Purpose: Control thermostat temperature and modes.

```python
# How to use:

#########################################################################
# All methods return "ERROR" or "CONNECTION_ERROR" if there is an error #
#########################################################################

# get current mode of Nest Thermostat 
# returns string ("COOL" -OR- "HEAT" -OR- "OFF")
get_current_temp_mode()

# get current temp 
# returns int (mode="OFF" -> 0 -OR- mode="HOT" or "COOL" -> temperature)
get_current_temp()

# parameter 1: value - int{set-temperature via [number]} -OR- string{set-mode via ["OFF", "HOT", "COOL"]}
# parameter 2: command - string{"SetCool", "SetHeat", "SetMode"}
# info 1: "SetCool", "SetHeat" are used alongside temperature number
# info 2: "OFF", "HOT", "COOL" used alongside "SetMode"
# Sample Method 1: update_thermostat(72, "SetCool" or "SetHeat")
# Sample Method 2: update_thermostat("OFF" or "HOT" or "COOL", "SetMode")
# returns nothing if successful
update_thermostat(value, command)
```

#### Spotify API
###### Purpose: Play a spotify playlist and control playback. 

```python
# How to use:

#########################################################################
# All methods return "ERROR" or "CONNECTION_ERROR" if there is an error #
########################  "SUCCESS OTHERWISE"  ##########################
#########################################################################

# starts/resumes playback
start_playback()

# pauses playback
pause_playback()

# skips to the next song in playback
skip_playback()

# goes back to previous song in playback
previous_playback()

# return playing status of device
is_playing()

# Change playback volume 
# paramter: increment - signed int{change volume via based on increment value}
change_volume(increment):
```

#### Kasa API
###### Purpose: Control a fan/light to turn ON or OFF.

```python
# turn Kasa SmartPlug ON or OFF
# fan/light is connected to SmartPlug so it will turn them OFF/ON
flip_switch(new_state)
```

## Git:
Make sure you have Git installed on your computer. Follow [thse steps](https://github.com/git-guides/install-git) if you dont have Git already.
```shell
# make sure you are in a directory that you want to put the project in
# make a copy of the repository on your computer
git clone https://github.com/Zracano/Gesture-Recognition
```


## Creating an environment:
[Instructions to install conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

The file **environment.yml** describes the python version and various dependencies with specific version numbers. 
To activate the environment perform the following in your command line:
```python
# creates the environment from the specifications file which only needs to be done once. 
conda env create -f environment.yml
# activates the environment which may need to be done each time you restart the terminal.
conda activate GestureRecognition
# test the environment installation where it will list all dependencies for that environment
conda env list
```


## How To Use
1. Follow the steps to [use git](#git) and clone the repository.
2. Follow the steps to [use conda](#creating-an-environment) to create a conda enviroment
3. Open nest_secrets.py, spotify_secrets.py, and kasa_secrets.py to add your API tokens
4. Make sure you have your camera turned on and applications have permision to use it
5. Run the gesture-detection-main.py script on your device

Finally use any of the following gestures to control your Home:

Spotify Gestures:
Thumb up   -> Start/Resume Song
Thumb down -> Pause Song
Right      -> Next Song
left       -> Previous Song

Nest Gestures:
ok 	 -> Change thermostat mode to COOL
two  -> Change thermostat mode to HEAT
fist -> Returns the current mode of thermostat

Kasa:
call + thumbs up   -> Turn on device
call + thumbs down -> Turn off device

Pattern Gesture:
Spotify Playing:
Clockwise Circle         -> Increase Volume
Counter-Clockwise Circle -> Decrease Volume

Spotify Not-Playing:
Clockwise Circle         -> Increase Thermostat Temp
Counter-Clockwise Circle -> Decrease Thermostat Temp

![Alt text](Gestures.png)
