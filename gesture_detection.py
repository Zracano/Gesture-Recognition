import concurrent.futures
import enum
import math

import cv2
import mediapipe as mp
from mediapipe.python.solutions.hands import HandLandmark


class HandLandmark(enum.IntEnum):
    """The 21 hand landmarks."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


def init():
    return mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)


def run(image, hands):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(detect_gesture, image, hands)
        return future.result()


# function to calculate distance between two landmarks
def calculate_distance(landmark1, landmark2):
    return math.hypot(landmark1.x - landmark2.x, landmark1.y - landmark2.y)


# write function documentation
def detect_gesture(image, hands):
    """
    Detects the gesture of the hand in the image
    :param image:
    :param hands:
    :return: string of gesture
    """
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hand_landmarks = hands.process(image).multi_hand_landmarks
    if not hand_landmarks:
        return None
    hand_landmarks = hand_landmarks[0]
    # recognize gestures
    # left screen is 1 and right screen is 0
    # top of screen is 0 and bottom of screen is 1
    # return the gesture detected or none

    if hand_landmarks.landmark[HandLandmark.THUMB_TIP].y < hand_landmarks.landmark[
        HandLandmark.THUMB_IP].y < \
            hand_landmarks.landmark[HandLandmark.THUMB_MCP].y < \
            hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y < hand_landmarks.landmark[
        HandLandmark.PINKY_MCP].y and hand_landmarks.landmark[HandLandmark.PINKY_TIP].x < hand_landmarks.landmark[HandLandmark.PINKY_PIP].x:
        return "up"
    # recognize thumbs down
    max_x = max(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].x,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].x,
                hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP].x,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].x)
    if hand_landmarks.landmark[HandLandmark.THUMB_TIP].y > hand_landmarks.landmark[
        HandLandmark.THUMB_IP].y > \
            hand_landmarks.landmark[HandLandmark.THUMB_MCP].y > \
            hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y > hand_landmarks.landmark[
        HandLandmark.PINKY_MCP].y and \
            not (hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].x > max_x or
                 hand_landmarks.landmark[
                     HandLandmark.MIDDLE_FINGER_TIP].x > max_x or
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].x > max_x or
                 hand_landmarks.landmark[
                     HandLandmark.PINKY_TIP].x > max_x):
        return "down"
    # recognize fist
    max_y = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].y,
                hand_landmarks.landmark[13].y,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].y)
    max_y2 = min(hand_landmarks.landmark[HandLandmark.THUMB_IP].y,
                 hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.PINKY_TIP].y)
    diff_4_9 = calculate_distance(hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP],
                                  hand_landmarks.landmark[HandLandmark.THUMB_TIP])
    if max_y2 > max_y and diff_4_9 < 0.15:
        return "fist"
    # recognize OK
    diff_4_8 = calculate_distance(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP],
                                  hand_landmarks.landmark[HandLandmark.THUMB_TIP])
    max_y = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].y,
                hand_landmarks.landmark[13].y,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].y)
    max_y2 = max(hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.PINKY_TIP].y)
    if diff_4_8 < 0.05 and max_y2 < max_y:
        return "ok"

    # recognize thumb pointing left
    max_y = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].y)
    max_y2 = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.PINKY_TIP].y)
    diff_4_5 = calculate_distance(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP],
                                  hand_landmarks.landmark[HandLandmark.THUMB_TIP])
    if hand_landmarks.landmark[HandLandmark.THUMB_TIP].x > hand_landmarks.landmark[
        HandLandmark.THUMB_IP].x > \
            hand_landmarks.landmark[HandLandmark.THUMB_MCP].x and max_y2 > max_y and max_y < hand_landmarks.landmark[
        HandLandmark.WRIST].y and \
            hand_landmarks.landmark[HandLandmark.THUMB_CMC].y > hand_landmarks.landmark[
        HandLandmark.PINKY_MCP].y and diff_4_5 > 0.1 and \
            hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y < hand_landmarks.landmark[HandLandmark.WRIST].y:
        return "left"
    # recognize thumb pointing right
    max_y = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].y)
    max_y2 = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.PINKY_TIP].y)
    if hand_landmarks.landmark[HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[
        HandLandmark.THUMB_IP].x < \
            hand_landmarks.landmark[HandLandmark.THUMB_MCP].x < hand_landmarks.landmark[
        HandLandmark.THUMB_CMC].x and max_y2 > max_y and \
            hand_landmarks.landmark[HandLandmark.THUMB_TIP].y < hand_landmarks.landmark[
        HandLandmark.WRIST].y and max_y < hand_landmarks.landmark[HandLandmark.WRIST].y:
        return "right"
    # recognize Call sign
    max_y = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP].y,
                hand_landmarks.landmark[HandLandmark.PINKY_MCP].y)
    max_y2 = min(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP].y,
                 hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y)
    diff_4_20 = calculate_distance(hand_landmarks.landmark[HandLandmark.PINKY_TIP],
                                   hand_landmarks.landmark[HandLandmark.THUMB_TIP])
    diff_20_13 = calculate_distance(hand_landmarks.landmark[HandLandmark.PINKY_TIP],
                                    hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP])
    if max_y2 > max_y and diff_4_20 > 0.2 and diff_20_13 > 0.14:
        return "call"
    # recognize two fingers up
    diff_8_12 = calculate_distance(hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP],
                                   hand_landmarks.landmark[HandLandmark.MIDDLE_FINGER_TIP])
    diff_4_16 = calculate_distance(hand_landmarks.landmark[HandLandmark.THUMB_TIP],
                                   hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP])
    if hand_landmarks.landmark[HandLandmark.PINKY_TIP].y > hand_landmarks.landmark[HandLandmark.RING_FINGER_MCP].y and \
            hand_landmarks.landmark[HandLandmark.RING_FINGER_TIP].y > hand_landmarks.landmark[
        HandLandmark.MIDDLE_FINGER_MCP].y and \
            diff_8_12 < 0.08 and diff_4_16 < 0.08:
        return "two"

    return None
