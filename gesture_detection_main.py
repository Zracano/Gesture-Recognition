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

def main():
    # initialize pattern detection
    pattern_detection_data = pattern_detection.init()
    gesture_detector_data = gesture_detection.init()
    # begin capture of video
    cap = cv2.VideoCapture(0)
    gesture_list = []
    last_command = ""
    
    while True:
        # read current frame from camera
        _, img = cap.read()

        # detect is a circle pattern is recognized
        pattern_detection.run(img, pattern_detection_data)
        
        # detect if a gesture is recognized and push it into the queue
        gesture_list.append(gesture_detection.run(img, gesture_detector_data))
        # handle gesture if found
        gesture_found = handle_gestures(gesture_list, last_command)
        
        # if gesture was found, clear gesture_list
        if gesture_found:
            # clear the list
            gesture_list.clear()
            # stores last command, used to handle call + (up or down) gesture command
            if gesture_found is not True and last_command not in ['up', 'down']:
                last_command = gesture_found
        # reset last command if call + gesture (up or down) command was ran already
        elif gesture_found == "" and last_command == "call":
            last_command = ""
            
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
    responses = [nest._Helper.ERROR, nest._Helper.CONNECTION_ERROR]
    frames = 12
    # check if the gesture has been detected for a certain amount of frames
    if len(gesture_list) >= frames:
        if gesture_list.count(gesture_list[0]) == len(gesture_list) and gesture_list[0] is not None:
            current_gesture = gesture_list[0]
            # run command based on current gesture
            # gesture thumbs up 
            if current_gesture == "up":
                # if last command is call
                # flip the kasa switch on
                if last_command == "call":
                    print(f"Call + Up Gesture Detected -> Kasa Switch -> ON")
                    response = kasa.flip_switch(1)
                    # notify user if an error occurs
                    if response in responses:
                        text_to_speech.run("Issue changing status of kasa")
                    return ""
                else:
                    # start spotify playback
                    response = spotify.start_playback()
                    print(f"Spotify -> Start Playback")
            # gesture thumbs down
            elif current_gesture == "down":
                # if last command is call
                # flip the kasa switch off
                if last_command == "call":
                    print(f"Call + Down Gesture Detected -> Kasa Switch -> OFF")
                    response = kasa.flip_switch(0)
                    # notify user if an error occurs
                    if response in responses:
                         text_to_speech.run("Issue changing status of kasa")
                    return ""
                else:
                    spotify.pause_playback()
                    print("Spotify -> Pause Playback")
            # gesture right
            elif current_gesture == "right":
                spotify.skip_playback()
                print("Spotify -> Next Song")
            # gesture left  
            elif current_gesture == "left":
                spotify.previous_playback()
                print("Spotify -> Previous Song")
            # gesture ok
            elif current_gesture == "ok":
                response = nest.update_thermostat(nest._Helper.COOL, nest._Helper.CHANGE_MODE_COMMAND)
                if response in responses:
                    # notify user if an error occurs
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
                    print("Thermostat Mode Set -> COOL")
            # gesture two
            elif current_gesture == "two":
                response = nest.update_thermostat(nest._Helper.HEAT, nest._Helper.CHANGE_MODE_COMMAND)
                if response in responses:
                    # notify user if an error occurs
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
                    print("Thermostat Mode Set -> HEAT")
            # gesture fist
            elif current_gesture == "fist":
                response = nest.get_current_temp_mode()
                if response in responses:
                    # notify user if an error occurs
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {response}")
                    print(f"Thermostat Mode -> {response}")
            # gesture call
            elif current_gesture == "call":
                # call by itself does nothing
                # it needs to be used with UP or DOWN Thumb Gesture
                # notify user that call gesture was detected
                text_to_speech.run(f"Call Gesture Detected")
                return "call"
            
        return True
    
    return False


if __name__ == '__main__':
    main()
