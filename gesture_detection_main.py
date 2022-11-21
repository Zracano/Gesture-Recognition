import cv2

import gesture_detection
import pattern_detection

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

    while True:
        # read current frame from camera
        _, img = cap.read()

        # detect is a circle pattern is recognized
        pattern_detection.run(img, pattern_detection_data)
        gesture = gesture_detection.run(img, gesture_detector_data)
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


if __name__ == '__main__':
    main()
