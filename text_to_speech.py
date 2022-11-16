from gtts import gTTS
from mutagen.mp3 import MP3
from threading import Thread
from time import sleep
import time
import os

# -------------------------------------------------------
# Program simply converts text to speech and plays it
# -------------------------------------------------------

# run in a different thread so it runs concurrently
def run(text):
    thread = Thread(target = text_to_speech, args = (text, ))
    thread.start()

def text_to_speech(text):
    # ensure filename is unique
    filename = f"output_{time.time()}.mp3"
    
    # convert text to speech
    try:
        audio = gTTS(text=text, lang="en", slow=False)
    except: 
        # there might not be an internet connection
        return
    
    # save text to speech in a mp3 file
    audio.save(filename)
    # start playing audio file
    os.system(f"start {filename}")
    # delete file after it was played
    delete_file(filename)
    
# delete audio file after it has been played
def delete_file(filename):
    if os.path.isfile(filename):
        # get duration of audio file
        audio_duration = MP3(filename).info.length
        # delay is added to ensure audio file has been played
        sleep(audio_duration)
        os.remove(filename)
    else: 
        print(f"Error: {filename} audio-file not found")