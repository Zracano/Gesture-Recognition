import cv2
import gesture_detection
import pattern_detection
import spotify
import nest
import text_to_speech
import kasa

'''
    SDSU [Fall 2022] - CS530 (Systems Programming)

    Group: 
    [Amar Khanshali] [Edgar Navarro] [Thu Vu] [Isaac Pompa]

    Project - Gesture-Based Home Control:
    Control your home using predetermined hand gestures without having to get up from your seat.
    Features include: turn a device (like a fan or light) on/off, changing thermostat mode and 
    adjust the temperature by simply doing a circle pattern, and playing your favorite playlist
    from spotify and changing/pausing songs.

    Date Created   :  Oct 12, 2022
    Date Completed : Nov 28, 2022
'''

class Data:
    responses = [nest._Helper.ERROR, nest._Helper.CONNECTION_ERROR]
    frames = 12
    gestures = ["up", "down", "left", "right", "fist", "ok", "two", "call"]
    EMPTY = None

def main():
    # initialize pattern detection
    pattern_detection_data = pattern_detection.init()
    gesture_detector_data = gesture_detection.init()
    # begin capture of video
    cap = cv2.VideoCapture(1)
    gesture_list = []
    last_command = ""
    
    while True:
        # read current frame from camera
        _, img = cap.read()
        
        # detect if a gesture is recognized and push it into the queue
        current_gesture = gesture_detection.run(img, gesture_detector_data)
        
        if current_gesture is not None:
            gesture_list.append(current_gesture)
        
        # if at least 12 frames were found
        if len(gesture_list) >= Data.frames and gesture_list.count(gesture_list[len(gesture_list)-1]) >= Data.frames:
            # handle gesture if found
            gesture_found = handle_gestures(gesture_list, last_command)
            # a gesture was found
            if gesture_found in Data.gestures:
                # clear the gesture list
                gesture_list.clear()
                # stores last command, used to handle call + (up or down or first) gesture command
                if gesture_found == "call":
                    last_command = gesture_found
                # reset last command if call + gesture (up or down) command was ran already
                elif gesture_found in ["up", "down", "fist"] and last_command == "call":
                    last_command = ""
                    
        # detect is a circle pattern is recognized
        pattern_detection.run(img, pattern_detection_data)
            
        ############## FOR DEMO PURPOSES ##############
        # show window (this will contain the gesture path)
        cv2.imshow("Pattern Canvas", pattern_detection_data.canvas)
        # show window (basic camera view)
        cv2.imshow("camera", img)
        
        # press 'q' to exit program
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    # release resource and close windows
    cap.release()
    cv2.destroyAllWindows()


# if a gesture was detected for a certain number of frames
# then run its' respective API call
def handle_gestures(gesture_list, last_command):
    current_gesture = gesture_list[len(gesture_list)-1]
    # run command based on current gesture
    # gesture thumbs up 
    if current_gesture == "up":
        # if last command is call
        # flip the kasa switch on
        if last_command == "call":
            print(f"Call + Up Gesture Detected -> Kasa Switch -> ON")
            response = kasa.flip_switch(1)
            # notify user if an error occurs
            if response in Data.responses:
                text_to_speech.run("Issue changing status of kasa")
        else:
            # start spotify playback
            response = spotify.start_playback()
            print(f"Spotify -> Start Playback")
        return "up"
    # gesture thumbs down
    elif current_gesture == "down":
        # if last command is call
        # flip the kasa switch off
        if last_command == "call":
            print(f"Call + Down Gesture Detected -> Kasa Switch -> OFF")
            response = kasa.flip_switch(0)
            # notify user if an error occurs
            if response in Data.responses:
                 text_to_speech.run("Issue changing status of kasa")
        else:
            spotify.pause_playback()
            print("Spotify -> Pause Playback")
        return "down"
    # gesture right
    elif current_gesture == "right":
        spotify.skip_playback()
        print("Spotify -> Next Song")
        return "right"
    # gesture left  
    elif current_gesture == "left":
        spotify.previous_playback()
        print("Spotify -> Previous Song")
        return "left"
    # gesture ok
    elif current_gesture == "ok":
        response = nest.update_thermostat(nest._Helper.COOL, nest._Helper.CHANGE_MODE_COMMAND)
        if response in Data.responses:
            # notify user if an error occurs
            text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
        else:
            text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
            print("Thermostat Mode Set -> COOL")
        return "ok"
    # gesture two
    elif current_gesture == "two":
        response = nest.update_thermostat(nest._Helper.HEAT, nest._Helper.CHANGE_MODE_COMMAND)
        if response in Data.responses:
            # notify user if an error occurs
            text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
        else:
            text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
            print("Thermostat Mode Set -> HEAT")
        return "two"
    # gesture fist
    elif current_gesture == "fist":
        # if last command is call
        # turn of thermostat
        if last_command == "call":
            response = nest.update_thermostat(nest._Helper.OFF, nest._Helper.CHANGE_MODE_COMMAND)
            if response in Data.responses:
                # notify user if an error occurs
                text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
            else:
                text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
                print("Thermostat Mode Set -> OFF")
        else:
            # if last command is not a fist, get current mode of Nest thermostat
            response = nest.get_current_temp_mode()
            if response in Data.responses:
                # notify user if an error occurs
                text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
            else:
                text_to_speech.run(f"Thermostat mode is currently set to {response}")
                print(f"Thermostat Mode -> {response}")
        return "fist"
    # gesture call
    elif current_gesture == "call":
        # call by itself does nothing
        # it needs to be used with UP or DOWN or FIST Gesture
        # notify user that call gesture was detected
        text_to_speech.run(f"Call Gesture Detected")
        return "call"



if __name__ == '__main__':
    main()
