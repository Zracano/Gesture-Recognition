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

    Date Created : Oct 12, 2022
'''


def main():
    # initialize pattern detection
    pattern_detection_data = pattern_detection.init()
    gesture_detector_data = gesture_detection.init()
    # begin capture of video
    cap = cv2.VideoCapture(0)
    gesture_list = []
    frames = 8
    
    while True:
        # read current frame from camera
        _, img = cap.read()

        # detect is a circle pattern is recognized
        pattern_detection.run(img, pattern_detection_data)
        
        # detect if a gesture is recognized and push it into the queue
        gesture_list.append(gesture_detection.run(img, gesture_detector_data))
        # handle gesture if found
        gesture_found = handle_gestures(gesture_list, frames)
        if gesture_found:
            # clear the list
            gesture_list.clear()
            
        ############## FOR TESTING PURPOSES ##############
        ############  REMOVING AFTER TESTING  ############
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


def handle_gestures(gesture_list, frames):
    responses = [nest._Helper.ERROR, nest._Helper.CONNECTION_ERROR]
    # check if the gesture has been detected for a certain amount of frames
    if len(gesture_list) >= frames:
        if gesture_list.count(gesture_list[0]) == len(gesture_list) and gesture_list[0] is not None:
            current_gesture = gesture_list[0]
            # run command based on current gesture
            if current_gesture == "up":
                spotify.start_playback()
            elif current_gesture == "down":
                spotify.pause_playback()
            elif current_gesture == "right":
                spotify.skip_playback()
            elif current_gesture == "left":
                spotify.previous_playback()
            elif current_gesture == "ok":
                response = nest.update_thermostat(nest._Helper.COOL, nest._Helper.CHANGE_MODE_COMMAND)
                if response in responses:
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
            elif current_gesture == "two":
                response = nest.update_thermostat(nest._Helper.HEAT, nest._Helper.CHANGE_MODE_COMMAND)
                if response in responses:
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {nest.get_current_temp_mode()}")
            elif current_gesture == "fist":
                response = nest.get_current_temp_mode()
                if response in responses:
                    text_to_speech.run(pattern_detection.Helper.THERMOSTAT_ERROR_MESSAGE)
                else:
                    text_to_speech.run(f"Thermostat mode is currently set to {response}")
            elif current_gesture == "call":
                # kasa.flip_switch()
                pass
        return True
    return False


if __name__ == '__main__':
    main()
