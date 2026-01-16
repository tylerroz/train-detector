import cv2
import numpy as np
import time
import json
from collections import deque

# load config
with open("cam_config.json", "r") as f:
    config = json.load(f)

RTSP_URL = config["rtsp_url"]
roi_cfg = config["roi"]
ROI = (roi_cfg["x1"], roi_cfg["y1"], roi_cfg["x2"], roi_cfg["y2"])

# motion detection constants
MOTION_AREA_THRESHOLD = 200           # min pixels to count as motion
START_FRAMES = 10                     # consecutive frames to start motion
STOP_FRAMES = 20                      # consecutive still frames to stop motion
MOVING_AVG_FRAMES = 5                 # frames to smooth motion area
TRAIN_PERSISTENCE_FRAMES = 20         # frames to confirm train presence

# helper function for camera read with ROI
def camera_read(cap, roi):
    ret, frame = cap.read()
    if not ret or frame is None or frame.sum() == 0:
        return None
    x1, y1, x2, y2 = roi
    h, w = frame.shape[:2]
    x1, x2 = max(0, min(x1, w-1)), max(0, min(x2, w))
    y1, y2 = max(0, min(y1, h-1)), max(0, min(y2, h))
    if x2 <= x1 or y2 <= y1:
        return None
    return frame[y1:y2, x1:x2], frame

# used to detect motion in ROI
def motion_detection(roi_frame, bg_subtractor, kernel, avg_history):
    mask = bg_subtractor.apply(roi_frame, learningRate=0.001)
    _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (15,3)), iterations=1)

    motion_area = cv2.countNonZero(mask)
    avg_history.append(motion_area)
    if len(avg_history) > MOVING_AVG_FRAMES:
        avg_history.popleft()
    avg_area = sum(avg_history)/len(avg_history)
    return mask, avg_area

# determine if motion detected is a train
# right now, do this is there is sustained horizontal motion
def train_presence_gate(mask, state):
    # compute motion_ratio
    motion_pixels = np.sum(mask > 0)
    motion_ratio = motion_pixels / (mask.shape[0] * mask.shape[1])

    # compute width_ratio
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(np.vstack(contours))
        width_ratio = w / mask.shape[1]
    else:
        width_ratio = 0

    # update persistence
    if motion_ratio > 0.35 and width_ratio > 0.6:
        state['persistence'] += 1
    else:
        state['persistence'] = 0

    train_present = state['persistence'] >= TRAIN_PERSISTENCE_FRAMES
    return train_present, state

def main():
    
    # setup capture from the network camera
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")

    bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    avg_history = deque()
    state = {'persistence': 0}

    motion_frames = 0
    still_frames = 0
    motion_active = False
    train_present = False

    while True:
        result = camera_read(cap, ROI)
        if result is None:
            time.sleep(0.05)
            continue
        roi_frame, full_frame = result

        # continually detect motion
        mask, avg_area = motion_detection(roi_frame, bg, kernel, avg_history)

        if avg_area > MOTION_AREA_THRESHOLD:
            motion_frames += 1
            still_frames = 0
        else:
            still_frames += 1
            motion_frames = 0

        if not motion_active and motion_frames >= START_FRAMES:
            motion_active = True
            print("Motion START detected")

        # if there was motion, check for train presence first
        if motion_active:
            train_present, state = train_presence_gate(mask, state)
            if train_present:
                print("Train is present!")

        # then handle motion end
        if motion_active and still_frames >= STOP_FRAMES:
            motion_active = False
            if train_present:
                train_present = False
                state['persistence'] = 0
                print("Train is gone.")
            print("Motion END detected")

        # show camera with ROI rectangle and motion mask
        x1, y1, x2, y2 = ROI
        cv2.rectangle(full_frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.imshow("Full Frame", full_frame)
        cv2.imshow("Motion Mask", mask)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
