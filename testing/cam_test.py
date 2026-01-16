import cv2
import time
import json

# Load config
with open("cam_config.json", "r") as f:
    config = json.load(f)

RTSP_URL = config["rtsp_url"]

def open_stream(url):
    """Open the RTSP stream and return the capture object."""
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Failed to connect to stream, retrying...")
        return None
    # Reduce buffering to get live frames
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

cap = open_stream(RTSP_URL)

while True:
    if cap is None:
        # Try reconnecting every 2 seconds
        time.sleep(2)
        cap = open_stream(RTSP_URL)
        continue

    ret, frame = cap.read()
    if not ret:
        print("Frame grab failed, reconnecting...")
        cap.release()
        cap = None
        continue

    cv2.imshow("Network Cam", frame)

    # Press ESC to quit
    if cv2.waitKey(1) == 27:
        break

# Clean up
if cap is not None:
    cap.release()
cv2.destroyAllWindows()