import cv2
import numpy as np
from collections import deque
from constants import TrainDirection

class MotionDetector:
    def __init__(
        self,
        motion_threshold=200,
        moving_avg_frames=5,
        centroid_history_frames=12,
        min_coverage=0.35
    ):
        self.motion_threshold = motion_threshold
        self.avg_history = deque(maxlen=moving_avg_frames)

        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=250,
            varThreshold=15,
            detectShadows=False
        )

        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        self.centroid_history = deque(maxlen=centroid_history_frames)
        self.locked_direction = None

        self.min_coverage = min_coverage
        
        self.motion_energy = None
        self.energy_decay = 0.9      # ~1–1.5s decay at ~20fps
        self.energy_threshold = 1.5  # how persistent motion must be

    def reset(self):
        """Call this when a train fully clears."""
        self.avg_history.clear()
        self.centroid_history.clear()
        self.locked_direction = None
        self.motion_energy = None

    def detect(self, roi_frame, freeze_bg=False):
        # background subtraction
        learning_rate = 0 if freeze_bg else 0.001
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor.apply(gray, learningRate=learning_rate)

        _, mask = cv2.threshold(mask, 120, 255, cv2.THRESH_BINARY)
        
        # initialize motion energy lazily
        if self.motion_energy is None:
            self.motion_energy = np.zeros(mask.shape, dtype=np.float32)

        # decay existing motion
        self.motion_energy *= self.energy_decay

        # reinforce where new motion appears
        self.motion_energy[mask > 0] += 1.0

        # clamp to prevent runaway growth
        np.clip(self.motion_energy, 0, 5.0, out=self.motion_energy)

        # rebuild mask from energy
        mask = (self.motion_energy > self.energy_threshold).astype(np.uint8) * 255
        
        # morph cleanup
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        mask = cv2.dilate(
            mask,
            cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3)),
            iterations=1
        )

        # extract motion coords
        coords = cv2.findNonZero(mask)
        if coords is None:
            self.centroid_history.clear()
            self.avg_history.append(0)
            return mask, 0, self.locked_direction

        xs = coords[:, 0, 0]
        ys = coords[:, 0, 1]

        # care about horizontal coverage only
        roi_width = roi_frame.shape[1]
        coverage = (xs.max() - xs.min()) / roi_width

        if coverage < self.min_coverage:
            self.centroid_history.clear()
            self.avg_history.append(0)
            return mask, 0, self.locked_direction

        # help with direction tracking
        cx = int(xs.mean())
        self.centroid_history.append(cx)

        # motion area smoothing
        motion_area = cv2.countNonZero(mask)
        self.avg_history.append(motion_area)
        avg_area = sum(self.avg_history) / len(self.avg_history)

        # direction inference and locking
        direction = self._infer_horizontal_direction(roi_width)

        if direction and self.locked_direction is None:
            self.locked_direction = direction

        # need locked direction (unsure about this)
        if self.locked_direction is None:
            avg_area = 0

        return mask, avg_area, self.locked_direction

    def _infer_horizontal_direction(self, roi_width):
        if len(self.centroid_history) < 6:
            return None

        dx = self.centroid_history[-1] - self.centroid_history[0]
        min_dx = int(roi_width * 0.1)  # proportional threshold

        if abs(dx) < min_dx:
            return None

        # southbound is left-to-right
        return TrainDirection.SOUTHBOUND if dx > 0 else TrainDirection.NORTHBOUND
