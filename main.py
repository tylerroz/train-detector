import time
import cv2
import json
import sys

from camera import open_camera, read_frame
from motion import MotionDetector
from notifications import notify_train_arrived, notify_train_gone
from train_gate import TrainGate

# Program config
debug = 'debug' in sys.argv
should_notify = 'notify' in sys.argv

# Load config
with open("cam_config.json", "r") as f:
    config = json.load(f)

RTSP_URL = config["rtsp_url"]
roi_cfg = config["roi"]
ROI = (roi_cfg["x1"], roi_cfg["y1"], roi_cfg["x2"], roi_cfg["y2"])

# Motion & train settings
START_FRAMES = 10
STOP_FRAMES = 20
MOTION_AREA_THRESHOLD = 200

def main():
    print("Starting train detection...")
    print("Arguments:")
    print("  debug (enables verbose output and visualization):", debug)
    print("  notify (enables push notifications):", should_notify)

    cap = open_camera(RTSP_URL)
    print("Camera stream initialized.")
    motion_detector = MotionDetector(motion_threshold=MOTION_AREA_THRESHOLD)
    print("Motion detector initialized.")
    train_gate = TrainGate()
    print("Train gate initialized.")
    
    print("Ready and looking for trains...")

    motion_frames = 0
    still_frames = 0
    motion_active = False

    while True:
        result = read_frame(cap, ROI)
        if result is None:
            time.sleep(0.05)
            continue
        roi_frame, full_frame = result

        # Freeze learning if train is present
        freeze_bg = train_gate.train_present
        mask, avg_area = motion_detector.detect(roi_frame, freeze_bg=freeze_bg)

        # Motion logic
        if avg_area > MOTION_AREA_THRESHOLD:
            motion_frames += 1
            still_frames = 0
        else:
            still_frames += 1
            motion_frames = 0

        # Motion start / stop
        if not motion_active and motion_frames >= START_FRAMES:
            motion_active = True
            if debug: print("Motion START detected")
        elif motion_active and still_frames >= STOP_FRAMES:
            motion_active = False
            if debug: print("Motion END detected")

        # Train gate update & edge detection
        prev_train, curr_train = train_gate.update(mask)
        if not prev_train and curr_train:
            print("Train START detected!")
            if should_notify: notify_train_arrived()
        elif prev_train and not curr_train:
            print("Train is GONE!")
            if should_notify: notify_train_gone()

        # Visualization
        if debug:
            x1, y1, x2, y2 = ROI
            cv2.rectangle(full_frame, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.imshow("Full Frame", full_frame)
            cv2.imshow("Motion Mask", mask)

        # Exit on ESC
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
