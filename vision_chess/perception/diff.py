import cv2
import numpy as np
from config import DIFF_THRESHOLD


def get_changed_squares(squares_before: dict, squares_after: dict) -> list[str]:
    """
    Compare deux états du plateau.
    Retourne la liste des cases dont le contenu a significativement changé.
    """
    changed = []
    for square, roi_after in squares_after.items():
        roi_before = squares_before.get(square)
        if roi_before is None:
            continue
        # S'assurer que les ROIs ont la même taille avant comparaison
        if roi_before.shape != roi_after.shape:
            roi_after = cv2.resize(roi_after, (roi_before.shape[1], roi_before.shape[0]))
        diff = cv2.absdiff(roi_before, roi_after)
        if diff.mean() > DIFF_THRESHOLD:
            changed.append(square)
    return changed