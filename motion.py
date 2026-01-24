import cv2
from collections import deque

class MotionDetector:
    def __init__(self, motion_threshold=200, moving_avg_frames=5):
        self.motion_threshold = motion_threshold
        self.avg_history = deque(maxlen=moving_avg_frames)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=40, detectShadows=False
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))

    def detect(self, roi_frame, freeze_bg=False):
        lr = 0 if freeze_bg else -1
        mask = self.bg_subtractor.apply(roi_frame, learningRate=lr)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, (7,3)), iterations=1)

        motion_area = cv2.countNonZero(mask)
        self.avg_history.append(motion_area)
        avg_area = sum(self.avg_history)/len(self.avg_history)
        return mask, avg_area