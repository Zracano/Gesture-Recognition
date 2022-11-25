import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import text_to_speech
import time
from threading import Thread
import spotify
import nest

'''
This program is able to detect a circular pattern made with the index finger along with the
rotation direction of the gesture.

The purpose of this program is to be able to take input via hand gestures instead of using
an app or speaking. The use case for this pattern detector is for changing the temperature 
of a NEST thermostat and or the volume of a speaker when playing music.

This is accomplished by following these steps:
1. Detect if the right hand is present in a image/frame and find the position of the index finger.
2. Make sure index finger is on top on all other fingers (aka you are pointing with your right index finger).
3. Follow the path of index finger by "drawing" the path on a window named "Pattern Canvas"
4. If the path comes back near the starting point, it is assumed that this MIGHT be a circle,
    therefore let cv2.HoughCircles() method determine if a circle was found.

Info: 
Some logic was added to handle jerky motions.

Limitations: 
1. On occasion, it cannot recognize the pattern right away, but it usually works on the second revolution.
2. Sometimes it deletes the pattern because it detects a jerk, probably due to processing speed. 

'''

def init():
    return Helper()

class Helper:  
    # constants
    WHITE = (255, 255, 255)
    END_RADIUS = 40
    DRAW_THICKNESS = 8
    IS_DRAW_OUT_OF_CIRCLE = False
    # max distance between coordinates
    MIN_POINTS = 30
    CLOCKWISE = "CLOCK-WISE"
    COUNTER_CLOCKWISE = "COUNTER-CLOCKWISE"
    NO_ROTATION = "NO-ROTATION"
    EMPTY_VALUE = -1
    TIME_BETWEEN_COMMANDS = 5
    EMPTY = 0
    RIGHT_HAND = "Right"
    HAND_DATA = "lmList"
    INCREMENT_SPOTIFY_VOLUME = 5
    INCREMENT_THERMOSTAT = 1
    
    # variables
    last_x1, last_y1 = EMPTY_VALUE, EMPTY_VALUE
    circle_points = []
    finger_color = WHITE
    rotation_direction = EMPTY
    last_command_time = EMPTY
    
    # voice replies
    THERMOSTAT_OFF_MESSAGE = "Thermostat is off, turn it on to change temperature"
    THERMOSTAT_ERROR_MESSAGE = "Issue connecting to nest device, try again later"
    
    def __init__(self):
        # setting up hand detector
        self.detector = HandDetector(maxHands=1, minTrackCon=0.75, detectionCon=0.75) 
        # create canvas (window) for the gestures
        self.canvas = np.zeros((500, 500), np.uint8)
    
    def clear_canvas(self):
        self.canvas = np.zeros((500, 500), np.uint8)
    
    @staticmethod
    def create_message(mode, temperature):
        return f"Thermostat mode is currently set to {mode} and the temperature is {temperature} degrees"
    
def run(img, program_data):   
    # run on a different thread
    thread = Thread(target = pattern_recognition, args =(img, program_data, ))
    thread.start()
    # wait until method is finished to proceed
    thread.join()

# returns the rotation direction (clockwise or counter-clockwise)
def getRotationDirection():
    if Helper.rotation_direction > 0:
        return Helper.CLOCKWISE
    elif Helper.rotation_direction < 0:
        return Helper.COUNTER_CLOCKWISE
    else:
        return Helper.NO_ROTATION

# determines if a circle pattern was drawn on "canvas"
def pattern_recognition(img, program_data):
    # flip the image so it is not invertered when "drawing" pattern
    img = cv2.flip(img, 1)
    # add hand skeleton to image to detect hand and differentiate between fingers
    hands, img = program_data.detector.findHands(img, flipType=False) 

    # gesture works ONLY on right hand, as this is sufficient for project
    if hands and hands[0]['type'] == Helper.RIGHT_HAND:
        if is_gesture_detected(hands[0][Helper.HAND_DATA]):
            # select index finger
            index_finger = hands[0][Helper.HAND_DATA][8]
            # find current position of index finger
            index_finger_pos = index_finger[0:2]
            # get the x and y coordinate of the index finger
            x1, y1 = index_finger_pos[0:2]
            
            # draw a dot at the current index finger position
            cv2.circle(program_data.canvas, index_finger_pos, Helper.DRAW_THICKNESS-5, Helper.finger_color, cv2.FILLED)

            # initialize last coordinates if they have not been set yet
            if Helper.last_x1 == Helper.EMPTY_VALUE and Helper.last_y1 == Helper.EMPTY_VALUE:
                Helper.last_x1, Helper.last_y1 = x1, y1   
                        
            # make sure that the last point is near the current point to prevent jerky motion
            if not abs(Helper.last_x1 - x1) > Helper.MIN_POINTS or not abs(Helper.last_y1 - y1) > Helper.MIN_POINTS:
                # draw a line between last point to current point
                cv2.line(program_data.canvas, (Helper.last_x1, Helper.last_y1), (x1, y1), Helper.finger_color, Helper.DRAW_THICKNESS)

                # prevent duplicate points
                if [x1, y1] not in Helper.circle_points:
                    Helper.circle_points.append([x1, y1])
                    # find the cross product of the last and current coordinate, this is 
                    # used to determine the rotation (clockwise (+) vs counter-clockwise (-))
                    # and all these rotations are added to determine the actual rotation of pattern
                    Helper.rotation_direction += ((Helper.last_x1 * y1) - (x1 * Helper.last_y1))
                
                # set the last coordinates to be the new coordinate of the index finger
                Helper.last_x1, Helper.last_y1 = x1, y1
                
                # determine if current point is near starting point
                dist = np.hypot(Helper.circle_points[0][0] - x1, Helper.circle_points[0][1] - y1)
                
                # checks if current point is near the starting point
                # this is to make sure that we check if the pattern is a circle
                # only if it going back around (much like a circle -> what is desired)
                # also check if user actually went out of the starting point area
                if dist**2 <= Helper.END_RADIUS**2 and Helper.IS_DRAW_OUT_OF_CIRCLE:
                    if is_circle_found(program_data):
                        # circle pattern was detected, ensure that there is 
                        # a delay between current and next command 
                        if time.time() - Helper.last_command_time > Helper.TIME_BETWEEN_COMMANDS:
                            Helper.IS_DRAW_OUT_OF_CIRCLE = False
                            # reset canvas since a circle was detected
                            reset_pattern(program_data)
                            api_call(getRotationDirection())
                            Helper.last_command_time = time.time()
                    else:
                        # circle not found
                        return
                elif dist**2 >= Helper.END_RADIUS**2:
                    # pattern draw is now out of starting circle
                    # IS_DRAW_OUT_OF_CIRCLE makes sure the "gesture" leaves the starting point
                    if not Helper.IS_DRAW_OUT_OF_CIRCLE:
                        Helper.IS_DRAW_OUT_OF_CIRCLE = True
            else:
                # jerky motion detected (distance between last and current point is not within 
                # threshold), therefore clearing drawing and allowing user to restart drawing pattern
                reset_pattern(program_data)
        else:
            # clear canvas if index finger is not up
            reset_pattern(program_data)
    
    return

# detects if index finger position is higher than all other fingers (aka index finger is up)
def is_gesture_detected(fingertip_positions):
    thumb, index_finger, middle_finger = fingertip_positions[4], fingertip_positions[8], fingertip_positions[12]
    ring_finger, pinky_finger = fingertip_positions[16], fingertip_positions[0]

    if index_finger[1] < min(middle_finger[1], ring_finger[1], pinky_finger[1], thumb[1]):
        return True
    else:
        False

# returns true if gesture path was similar to a circle, false otherwise
def is_circle_found(program_data):
    # make sure that the canvas is not null and there is at least one point drawn
    if program_data.canvas is None and len(Helper.circle_points) > Helper.EMPTY:
        return False

    try:
        # see if there is a circle found in canvas (the pattern drawn)
        circles = cv2.HoughCircles(program_data.canvas, cv2.HOUGH_GRADIENT, 
                                   1, 20, param1=30, param2=20, minRadius=0, maxRadius=0)          
    except:
        return False
    
    # if a circle was not found, return false
    if circles is None or len(circles) == 0:
        return False
    
    # else, return true since circles is not empty, indicating a circle pattern was found
    return True
    
# clear the gesture path on window and reset variables
def reset_pattern(program_data):
    program_data.clear_canvas()
    Helper.last_x1, Helper.last_y1 = Helper.EMPTY_VALUE, Helper.EMPTY_VALUE
    Helper.circle_points = []
    Helper.IS_DRAW_OUT_OF_CIRCLE = False
    
# determine which api to call in order to execute pattern gesture
def api_call(rotation_direction):
    is_increasing = True
    if rotation_direction == Helper.COUNTER_CLOCKWISE:
        is_increasing = False
        
    # if spotify is playing, increment/decrement the volume depending on pattern rotation
    if spotify.is_playing():
        new_volume = Helper.INCREMENT_SPOTIFY_VOLUME * (1 if is_increasing else -1)
        spotify.change_volume(new_volume)
        print(f"Spotify: new volume -> {new_volume}")
    else:
        # change thermostat temperature if device is ON
        current_temp_mode = nest.get_current_temp_mode()
         # change thermostat temperature if device is ON and is set to either "HEAT" or "COOL"
        if current_temp_mode in [nest._Helper.COOL, nest._Helper.HEAT]:
            # get the command to change thermostat based on current thermostat mode
            current_mode = nest._Helper.COOL_COMMAND if current_temp_mode == nest._Helper.COOL else nest._Helper.HEAT_COMMAND
            # get current temperature
            current_temp = nest.get_current_temp()
            # change temperature (+1 or -1) based on pattern rotation
            response = nest.update_thermostat(current_temp + Helper.INCREMENT_THERMOSTAT, current_mode)
            # if there was an error, notify user
            if response in [nest._Helper.ERROR, nest._Helper.CONNECTION_ERROR]:
                text_to_speech.run(Helper.THERMOSTAT_ERROR_MESSAGE)
            else:
                # temperature updated, notify
                text_to_speech.run(Helper.create_message(current_temp_mode, current_temp))
        else:
            # thermostat device is off, notify user
            text_to_speech.run(Helper.THERMOSTAT_OFF_MESSAGE)