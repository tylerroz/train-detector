import time
import cv2
import database
import json
import sys

from camera import open_camera, read_frame
from helper import log
from motion import MotionDetector
from notifications import notify_train_arrived, notify_train_gone
from train_gate import TrainGate
from threading import Thread
from video_server import start_video_server, update_frame


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
    train_gate = TrainGate(
        persistence_frames = 45,
        grace_frames = 400, # camera is at 20fps
    )
    print("Train gate initialized.")
    
    try:
        database.get_conn()
    except Exception as e:
        print("ERROR: Could not connect to database:", e)
        return
    
    database.recover_open_events()
    print("Database connection verified.")
    
    video_thread = Thread(
        target=start_video_server,
        daemon=True
    )
    video_thread.start()
    last_stream_update_ts = 0
    print("Video stream available on http://<host>:8080/video")
        
    print("Ready and looking for trains...")

    train_timer = None
    prev_train_present = False

    while True:
        result = read_frame(cap, ROI)
        if result is None:
            time.sleep(0.05)
            continue

        roi_frame, full_frame = result

        prev_train_present = train_gate.train_present
        freeze_bg = train_gate.train_present

        mask, avg_area, direction = motion_detector.detect(
            roi_frame,
            freeze_bg=freeze_bg
        )

        train_present, state = train_gate.update(mask)

        if train_present and current_train_direction is None and direction is not None:
            current_train_direction = direction

        # train start
        if not prev_train_present and train_present:
            log("Train START detected!")
            train_timer = time.time()
            database.start_train_event()
            if should_notify:
                notify_train_arrived()

        # train end
        elif prev_train_present and not train_present:
            log("Train is GONE!")
            train_duration = time.time() - train_timer if train_timer else 0
            log(f"Train duration: {train_duration:.1f} seconds")
            database.end_train_event(
                direction=current_train_direction,
            )
            if should_notify:
                notify_train_gone()

            # Reset per-train state
            current_train_direction = None
            train_timer = None
            motion_detector.reset()


        # Visualization
        x1, y1, x2, y2 = ROI
        cv2.rectangle(full_frame, (x1,y1), (x2,y2), (0,255,0), 2)
        
        # Convert ROI mask to color
        colored_roi_mask = cv2.applyColorMap(mask, cv2.COLORMAP_JET)

        # Blend only the ROI part
        alpha = 0.4
        full_frame[y1:y2, x1:x2] = cv2.addWeighted(
            full_frame[y1:y2, x1:x2], 1.0, colored_roi_mask, alpha, 0
        )
            
        if debug:
            cv2.imshow("Full Frame", full_frame)
            cv2.imshow("Motion Mask", mask)
            # cv2.imshow("Overlayed Frame", overlayed_frame)
        
        # if current_train_direction:
        #     cv2.putText(frame, current_train_direction, (20,40),
        #         cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)        
        
        # this helps reduce CPU load by limiting live stream frame updates
        if time.time() - last_stream_update_ts > 1:
            update_frame(full_frame)
            last_stream_update_ts = time.time()

        # Exit on ESC
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
