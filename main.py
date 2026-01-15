import cv2
import time
import json

# Load config
with open("cam_config.json", "r") as f:
    config = json.load(f)

RTSP_URL = config["rtsp_url"]
roi_config = config["roi"]
ROI = (roi_config["x1"], roi_config["y1"], roi_config["x2"], roi_config["y2"])
MOTION_AREA_THRESHOLD = 50
START_FRAMES = 5
STOP_FRAMES = 10

def main():
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")

    bg = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=16,
        detectShadows=True
    )

    motion_frames = 0
    still_frames = 0
    motion_active = False

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
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

        # -------------------------------------------------
        # MOTION DETECTION
        # -------------------------------------------------
        mask = bg.apply(roi)

        mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)[1]
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, None, iterations=2)

        motion_area = cv2.countNonZero(mask)

        if motion_area > MOTION_AREA_THRESHOLD:
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

        # -------------------------------------------------
        # DEBUG VISUALIZATION
        # -------------------------------------------------
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("Frame", frame)
        cv2.imshow("Motion Mask", mask)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
