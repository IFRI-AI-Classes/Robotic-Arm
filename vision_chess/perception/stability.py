import cv2
import numpy as np
from config import STABILITY_THRESHOLD, STABILITY_FRAMES


class StabilityDetector:
    def __init__(self):
        self._buffer: list[np.ndarray] = []
        self.stable_count: int = 0

    def update(self, frame: np.ndarray) -> bool:
        """
        Reçoit une frame BGR.
        Retourne True si le plateau est stable depuis STABILITY_FRAMES frames.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self._buffer.append(gray)
        if len(self._buffer) > STABILITY_FRAMES:
            self._buffer.pop(0)

        if len(self._buffer) < 2:
            self.stable_count = 0
            return False

        diffs = [
            cv2.absdiff(self._buffer[i - 1], self._buffer[i]).mean()
            for i in range(1, len(self._buffer))
        ]
        stable = max(diffs) < STABILITY_THRESHOLD
        self.stable_count = self.stable_count + 1 if stable else 0
        return self.stable_count >= STABILITY_FRAMES

    def reset(self):
        self._buffer.clear()
        self.stable_count = 0