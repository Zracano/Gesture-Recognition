import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

class Helper:
    BLACK = (255, 255, 255)
    DRAW_THICKNESS = 10

def pattern_recognition():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(maxHands=1, minTrackCon=0.85, detectionCon=0.85)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False) # show skeleton
        # hands = detector.findHands(img, draw=False)
        canvas = np.zeros((500,500), np.uint8)
        
        if hands and hands[0]['type'] == "Right":
            is_gesture_detected(hands[0]['lmList'])
            index_finger = hands[0]['lmList'][8]
            index_finger_pos = index_finger[0:2]
            # add a dot on index finger on real image
            cv2.circle(img, index_finger_pos, Helper.DRAW_THICKNESS, Helper.BLACK, cv2.FILLED)
            # add a dot on index finger on black canvas
            cv2.circle(canvas, index_finger_pos, Helper.DRAW_THICKNESS, Helper.BLACK, cv2.FILLED)
            
        cv2.imshow("canvas", canvas)
        cv2.imshow("Image", img)
        
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
# detects if index finger is higher than all other fingers (aka index finger is up)
def is_gesture_detected(fingertip_positions):
    thumb, index_finger, middle_finger = fingertip_positions[4], fingertip_positions[8], fingertip_positions[12]
    ring_finger, pinky_finger = fingertip_positions[16], fingertip_positions[0]
    
    if index_finger[1] < min(middle_finger[1], ring_finger[1], pinky_finger[1], thumb[1]):
        print("Gesture Detected")
        True
    else:
        False

pattern_recognition()