import pattern_detection
import cv2

#
# CS530 Systems Programming
# Gesture-Based Home Control
# Date Created : Oct 12, 2022
# 


if __name__ == '__main__':
    # initialize canvas and variable(s) for pattern detection
    pattern_detection.init()
    
    # begin capture of video
    cap = cv2.VideoCapture(0)
    
    while True:
        # read current frame from camera
        _, img = cap.read()
        
        # detect is a circle pattern is recognized
        pattern_detection.run(img)
        
        ############## FOR TESTING PURPOSES ############## 
        ############  REMOVING AFTER TESTING  ############
        # show window (this will contain the gesture path)
        cv2.imshow("canvas", pattern_detection.Helper.canvas)
        # show window (basic camera view)
        # cv2.imshow("camera", img)
        # press 'q' to exit program
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    # release resource and close windows
    cap.release()
    cv2.destroyAllWindows()