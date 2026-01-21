import cv2
import numpy as np

class TrainGate:
    def __init__(
        self,
        start_motion_ratio=0.35,
        stop_motion_ratio=0.20,
        min_width_ratio=0.60,
        persistence_frames=25,
        grace_frames=30,
    ):
        self.start_motion_ratio = start_motion_ratio
        self.stop_motion_ratio = stop_motion_ratio
        self.min_width_ratio = min_width_ratio
        self.persistence_frames = persistence_frames
        self.grace_frames = grace_frames

        # this will help keep track of train presence, and allow for a cooldown with "grace frames"
        self.state = {
            "persistence": 0, # how many strong frames seen recently
            "grace": 0, # how long motion has been weak
            "train_present": False,
        }
    
    @property
    def train_present(self):
        return self.state["train_present"]
        
    def update(self, mask):
        """
        Returns:
            train_present (bool)
            state (dict)
        """

        h, w = mask.shape
        motion_pixels = cv2.countNonZero(mask)
        motion_ratio = motion_pixels / (h * w)

        # How wide is motion across the ROI?
        cols_with_motion = np.any(mask > 0, axis=0)
        motion_width = np.sum(cols_with_motion)
        width_ratio = motion_width / w

        strong_motion = (
            motion_ratio >= self.start_motion_ratio
            and width_ratio >= self.min_width_ratio
        )

        weak_motion = motion_ratio < self.stop_motion_ratio

        # ----------------------------
        # TRAIN START LOGIC
        # ----------------------------
        if strong_motion:
            self.state["persistence"] += 1
        elif weak_motion:
            self.state["persistence"] = max(0, self.state["persistence"] - 1)

        if (
            not self.state["train_present"]
            and self.state["persistence"] >= self.persistence_frames
        ):
            self.state["train_present"] = True
            self.state["grace"] = 0

        # ----------------------------
        # TRAIN END LOGIC (GRACE)
        # ----------------------------
        if self.state["train_present"]:
            if weak_motion:
                self.state["grace"] += 1
            else:
                self.state["grace"] = 0

            if self.state["grace"] >= self.grace_frames:
                self.state["train_present"] = False
                self.state["persistence"] = 0
                self.state["grace"] = 0

        return self.state["train_present"], self.state
