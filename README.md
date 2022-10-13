# Gesture Recognition

Git (Step 1):
```Shell Session
# SETTING UP
# ---- ASSUMING you have Git installed ----
# using git bash (command line)
# make sure you are in a directory that you want to put the project in
# make a copy on your computer
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

```

Recommendations for those using Windows (Step 2):<br>
Google the respective commands for Unix
```Shell Session
# add a virtual enviroment for the project (make sure you are in the Gesture-Recognition directory)
python3 python -m venv venv
```
```Shell Session
# activate your virtual enviroment
venv\Scripts\activate.bat
```
- download whatever packages you need using pip3
```Shell Session
# make sure you are up-to-date with the current requirements.txt on GitHub, if not, run these 2 commands
# git pull 
# pip install -r requirements.txt
pip3 freeze > requirements.txt
```
