# Gesture Recognition

## APIs

#### Nest API
###### Purpose: Control thermostat temperature and modes (HOT, COOL, OFF).

```python
# How to use:

#########################################################################
# All methods return "ERROR" or "CONNECTION_ERROR" if there is an error #
#########################################################################

# get current mode of Nest Thermostat
# returns: COOL, HEAT, or OFF
get_current_temp_mode()

# get current temp
# if current mode is HEAT or COOL, returns a temperature
# if mode is OFF, returns a 0
# returns: int (temperature value)
get_current_temp()

# change temperature: {value} = int and {command} = "SetCool" or "SetHeat"
# change temperature mode: {value} = "OFF", "HOT", or "COOL" and {command} = "SetMode"
# return nothing is successful
update_thermostat(value, command)
```

#### Spotify API

#### Kasa API

## Git:
```shell
# SETTING UP
# ---- ASSUMING you have Git installed ----
# using git bash (command line)
# make sure you are in a directory that you want to put the project in
# you can use cd and ls to navigate your computer's directories
# make a copy of the repository on your computer
git clone https://github.com/Zracano/Gesture-Recognition
# go inside project directory
cd Gesture-Recognition
# set the remote url so when u push/pull, it goes to GitHub
git remote set-url origin https://github.com/Zracano/Gesture-Recognition.git

# TO PUSH TO GITHUB REPO
# add files so that you can push to repo
git add .
# commit/confirm your changes
git commit -m "explain what you did, but please keep it nice and short"
# push your changes to Github
git push

# NICE TO KNOW COMMANDS
# see the status of the project files aka changed files
git status
# to get the most updated project files
git pull
# Always create a new branch when working on something new
git checkout -b {branch-name}
# To switch between different branches
git checkout {branch-name}
# To store local changes without committing
git stash 
# To restore local changes
git stash pop
```
## Creating an environment:
[Instructions to install conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

The file **environment.yml** describes the python version and various dependencies with specific version numbers. 
To activate the environment:

```shell
conda env create -f environment.yml

conda activate gesture_env

conda env list
```

The first line creates the environment from the specifications file which only needs to be done once. 

The second line activates the environment which may need to be done each time you restart the terminal.

The third line is to test the environment installation where it will list all dependencies for that environment

When you update your environment by using 

```shell
conda install
```

or 

```shell
pip install
```

we need to update our environment.yml file by doing
```shell
conda env export > environment.yml

# after this, go to environment.yml file and delete last line (starts with "prefix")

```

If we pull a new environment.yml file we simply update or environment by doing
```shell
conda env update --prefix ./env --file environment.yml  --prune
```


