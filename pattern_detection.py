import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

'''
----------------------------------------------------------------------
TESTING: uncomment line 177 or by calling pattern_recognition() method
----------------------------------------------------------------------
This program is able to detect a circular motion gesture with the index finger. 

The purpose of this program is to be able to take input via hand gestures instead of using
an app or speaking. The use case for this hand gesture is for changing the temperature of a NEST
thermostat and or the volume of a speaker.

This is accomplished by following these steps:
1. detect if there is a hand and find the index finger
2. make sure index finger is on top on all other fingers (aka you are pointing with your right index finger)
3. follow path of finger by "drawing" the path on a separate window named "canvas"
4. if the path comes back near the starting point, it is assumed that this MIGHT be a circle,
    therefore, send it to cv2.HoughCircles() and see if circle(s) were found
5. increment number of revolutions if found

Info: 
Some logic was added to handle jerky motions.

Limitations: 
1. sometimes it cannot recognize the pattern right away, but it usually works on the second revolution
2. sometimes it deletes the pattern because it detects a jerk, probably due to skipped frames

'''

class Helper:
    # constants
    BLACK = (255, 255, 255)
    ORANGE = (216, 83, 0)
    END_RADIUS = 35
    DRAW_THICKNESS = 10
    IS_DRAW_OUT_OF_CIRCLE = False
    MIN_POINTS = 40
    
    # variables
    last_x1, last_y1 = 0, 0
    canvas = ""
    num_revolutions = 0
    circle_points = []
    finger_color = BLACK

def pattern_recognition():
    # create canvas (window) for the gestures
    Helper.canvas = np.zeros([500, 500, 3], np.uint8)

    # begin capture of video
    cap = cv2.VideoCapture(0)
    # setting up hand detector
    detector = HandDetector(maxHands=1, minTrackCon=0.75, detectionCon=0.75)

    while True:
        _, img = cap.read()
        # flip the image so it is not invertered when "drawing"
        img = cv2.flip(img, 1)
        # show hand skeleton
        hands, img = detector.findHands(img, flipType=False) 
         # do not show hand skeleton
        # hands = detector.findHands(img, draw=False)

        if hands and hands[0]['type'] == "Right":
            if is_gesture_detected(hands[0]['lmList']):
                index_finger = hands[0]['lmList'][8]
                index_finger_pos = index_finger[0:2]
                Helper.finger_color = Helper.ORANGE

                # add a dot on index finger on real image
                cv2.circle(img, index_finger_pos, Helper.DRAW_THICKNESS, Helper.finger_color, cv2.FILLED)
                
                # font for text overlay
                font = cv2.FONT_HERSHEY_COMPLEX
                # put number of revolutions on window to view 
                # actually this is not a good idea because it will recognize circles in the word
                # Revolutions has an o in it, *sigh*, but will leave here for testing purposes 
                #cv2.putText(Helper.canvas, f"Revolutions - {Helper.num_revolutions}", (50,50), font, 1, Helper.ORANGE, 3)
                
                # draw
                x1, y1 = index_finger_pos[0:2]
                if Helper.last_x1 == 0 and Helper.last_y1 == 0:
                    Helper.last_x1, Helper.last_y1 = x1, y1   
                      
                # set the minimum amount of coordinates/points for the circle
                # also makes sure that the last point is near to current point to prevent jerky motion
                if not abs(Helper.last_x1- x1) > Helper.MIN_POINTS or not abs(Helper.last_y1 - y1) > Helper.MIN_POINTS:
                    cv2.line(Helper.canvas, (Helper.last_x1, Helper.last_y1), (x1, y1), Helper.finger_color, Helper.DRAW_THICKNESS)
                    Helper.last_x1, Helper.last_y1 = x1, y1
                    # prevent duplicates
                    if [x1, y1] not in Helper.circle_points:
                        Helper.circle_points.append([x1, y1])
                                        
                    # determine if current point is near starting point
                    dist = np.hypot(Helper.circle_points[0][0] - x1, Helper.circle_points[0][1] - y1)
                    
                    # checks if current line is inside circle
                    if dist**2 < Helper.END_RADIUS**2 or dist**2 == Helper.END_RADIUS**2:
                        # check if user actually when out of the starting circle
                        if Helper.IS_DRAW_OUT_OF_CIRCLE:
                            IS_DRAW_OUT_OF_CIRCLE = False
                            if is_circle_found():
                                Helper.num_revolutions+=1
                                clear_canvas()
                                print(f"Revolutions Detected: {Helper.num_revolutions}")
                            else:
                                continue
                    else:
                        # line is out of starting circle
                        # IS_DRAW_OUT_OF_CIRCLE makes sure the "gesture" leaves the starting point
                        if not Helper.IS_DRAW_OUT_OF_CIRCLE:
                            Helper.IS_DRAW_OUT_OF_CIRCLE = True
                else:
                    # jerky motion detected (distance between last and current point is not within 
                    # threshold), therefore clear drawing and allow user to restart
                    clear_canvas()
                
            else:
                # clear canvas if index finger is not up
                clear_canvas()
        else:
            # clear canvas if no hand is present/detected
            clear_canvas()
            # reset number of revolutions
            Helper.num_revolutions = 0
        

        # show window (this will contain the gesture path)
        cv2.imshow("canvas", Helper.canvas)
        # show window (camera view)
        cv2.imshow("camera", img)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    # release resource and close all windows
    cap.release()
    cv2.destroyAllWindows()

# detects if index finger is higher than all other fingers (aka index finger is up)
def is_gesture_detected(fingertip_positions):
    thumb, index_finger, middle_finger = fingertip_positions[4], fingertip_positions[8], fingertip_positions[12]
    ring_finger, pinky_finger = fingertip_positions[16], fingertip_positions[0]

    if index_finger[1] < min(middle_finger[1], ring_finger[1], pinky_finger[1], thumb[1]):
        return index_finger
    else:
        False

# returns True if gesture path was similar to a circle, false otherwise
def is_circle_found():
    if Helper.canvas is None or len(Helper.circle_points) < Helper.MIN_POINTS:
        return False

    try:
        circles = cv2.HoughCircles(Helper.canvas, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=22, minRadius=0, maxRadius=0)          
    except:
        return False
    
    # if no circle wa found, return false
    if circles is None or len(circles) == 0:
        return False
    
    # else, return true wince circles is not empty, indicating a circle pattern was found
    return True
    
# clear the gesture path on window and reset circle points
def clear_canvas():
    Helper.canvas = np.zeros((500, 500), np.uint8)
    Helper.last_x1, Helper.last_y1 = 0, 0 
    Helper.circle_points = []

# test this program by uncommenting (next line)    
# pattern_recognition()