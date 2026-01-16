import cv2
import numpy as np

class TrainGate:
    def __init__(self, persistence_frames=20):
        self.persistence_frames = persistence_frames
        self.state = {'persistence': 0}
        self.train_present = False

    def update(self, mask):
        """Return previous and current train state (for edge detection)"""
        prev_train = self.train_present
        self.train_present = self._compute_train_present(mask)
        return prev_train, self.train_present

    def _compute_train_present(self, mask):
        motion_pixels = np.sum(mask > 0)
        motion_ratio = motion_pixels / (mask.shape[0] * mask.shape[1])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x, y, w, h = cv2.boundingRect(np.vstack(contours))
            width_ratio = w / mask.shape[1]
        else:
            width_ratio = 0

        # Update persistence counter
        if motion_ratio > 0.35 and width_ratio > 0.6:
            self.state['persistence'] += 1
        else:
            self.state['persistence'] = 0

        return self.state['persistence'] >= self.persistence_frames
