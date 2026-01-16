import time
import cv2
import json

from camera import open_camera, read_frame
from motion import MotionDetector
from notifications import notify_train_arrived, notify_train_gone
from train_gate import TrainGate

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
    cap = open_camera(RTSP_URL)
    motion_detector = MotionDetector(motion_threshold=MOTION_AREA_THRESHOLD)
    train_gate = TrainGate()

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
            print("Motion START detected")
        elif motion_active and still_frames >= STOP_FRAMES:
            motion_active = False
            print("Motion END detected")

        # Train gate update & edge detection
        prev_train, curr_train = train_gate.update(mask)
        if not prev_train and curr_train:
            print("Train START detected!")
            notify_train_arrived()
        elif prev_train and not curr_train:
            notify_train_gone()

        # Visualization
        x1, y1, x2, y2 = ROI
        cv2.rectangle(full_frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.imshow("Full Frame", full_frame)
        cv2.imshow("Motion Mask", mask)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
