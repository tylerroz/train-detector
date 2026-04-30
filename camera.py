import cv2
import time

_RECONNECT_FAILURES = 10   # consecutive bad reads before reconnect attempt
_RECONNECT_BACKOFF  = 3.0  # seconds to wait between reconnect attempts

def open_camera(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10_000)
    cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10_000)
    if not cap.isOpened():
        raise RuntimeError("Failed to open camera stream")
    return cap


class ResilientCamera:
    def __init__(self, rtsp_url, roi):
        self.rtsp_url = rtsp_url
        self.roi = roi
        self._cap = open_camera(rtsp_url)
        self._fail_streak = 0

    def _reopen(self):
        print("Camera: stream lost, attempting reconnect...")
        try:
            self._cap.release()
        except Exception:
            pass
        time.sleep(_RECONNECT_BACKOFF)
        try:
            self._cap = open_camera(self.rtsp_url)
            self._fail_streak = 0
            print("Camera: reconnected successfully.")
        except RuntimeError as e:
            print(f"Camera: reconnect failed ({e}), will retry next cycle.")

    def read(self):
        ret, frame = self._cap.read()
        if not ret or frame is None or frame.sum() == 0:
            self._fail_streak += 1
            if self._fail_streak >= _RECONNECT_FAILURES:
                self._reopen()
            return None

        self._fail_streak = 0
        x1, y1, x2, y2 = self.roi
        h, w = frame.shape[:2]
        x1, x2 = max(0, min(x1, w - 1)), max(0, min(x2, w))
        y1, y2 = max(0, min(y1, h - 1)), max(0, min(y2, h))
        if x2 <= x1 or y2 <= y1:
            return None
        return frame[y1:y2, x1:x2], frame


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
