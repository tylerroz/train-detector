import cv2
import time
import json

# Load config
with open("cam_config.json", "r") as f:
    config = json.load(f)

RTSP_URL = config["rtsp_url"]
roi_config = config["roi"]
ROI = (roi_config["x1"], roi_config["y1"], roi_config["x2"], roi_config["y2"])

# -------------------------
# MOTION DETECTION SETTINGS
# -------------------------
MOTION_AREA_THRESHOLD = 200  # min pixels to count as motion
START_FRAMES = 10            # consecutive frames to start motion
STOP_FRAMES = 20             # consecutive still frames to stop motion
MOVING_AVERAGE_FRAMES = 5    # number of frames to smooth motion area

def main():
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")

    # Background subtractor
    bg = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=16,
        detectShadows=True
    )

    motion_frames = 0
    still_frames = 0
    motion_active = False
    motion_area_history = []

    # Morphology kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.sum() == 0:
            time.sleep(0.05)
            continue

        h, w = frame.shape[:2]
        x1, y1, x2, y2 = ROI
        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h))
        if x2 <= x1 or y2 <= y1:
            print("⚠️ Invalid ROI after clamping:", (x1, y1, x2, y2))
            continue

        roi = frame[y1:y2, x1:x2]

        # -------------------------
        # MOTION DETECTION
        # -------------------------
        mask = bg.apply(roi)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=3)

        motion_area = cv2.countNonZero(mask)

        # Moving average for smoothing
        motion_area_history.append(motion_area)
        if len(motion_area_history) > MOVING_AVERAGE_FRAMES:
            motion_area_history.pop(0)
        avg_motion_area = sum(motion_area_history) / len(motion_area_history)

        if avg_motion_area > MOTION_AREA_THRESHOLD:
            motion_frames += 1
            still_frames = 0
        else:
            still_frames += 1
            motion_frames = 0

        if not motion_active and motion_frames >= START_FRAMES:
            motion_active = True
            print("Motion START detected")

        if motion_active and still_frames >= STOP_FRAMES:
            motion_active = False
            print("Motion END detected")

        # -------------------------
        # DEBUG VISUALIZATION
        # -------------------------
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        cv2.imshow("Motion Mask", mask)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    