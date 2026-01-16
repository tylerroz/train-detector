import cv2

def open_camera(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")
    return cap

def read_frame(cap, roi):
    ret, frame = cap.read()
    if not ret or frame is None or frame.sum() == 0:
        return None
    x1, y1, x2, y2 = roi
    h, w = frame.shape[:2]
    x1, x2 = max(0, min(x1, w-1)), max(0, min(x2, w))
    y1, y2 = max(0, min(y1, h-1)), max(0, min(y2, h))
    if x2 <= x1 or y2 <= y1:
        return None
    roi_frame = frame[y1:y2, x1:x2]
    return roi_frame, frame
