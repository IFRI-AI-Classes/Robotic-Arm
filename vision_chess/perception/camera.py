import cv2
import numpy as np
import urllib.request
from config import CAMERA_URL, FRAME_WIDTH, FRAME_HEIGHT, TEST_MODE, TEST_IMAGE_PATH


def fetch_frame() -> np.ndarray | None:
    """
    Retourne une frame BGR.
    En TEST_MODE : charge depuis TEST_IMAGE_PATH sans resize (préserve le ratio).
    En prod      : fetch depuis l'IP webcam + resize.
    """
    if TEST_MODE:
        frame = cv2.imread(TEST_IMAGE_PATH)
        if frame is None:
            print(f"[camera] Image non trouvée : {TEST_IMAGE_PATH}")
            return None
        # Pas de resize forcé — on garde le ratio original
        return frame

    try:
        resp = urllib.request.urlopen(CAMERA_URL, timeout=3)
        img_np = np.frombuffer(resp.read(), dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if frame is None:
            return None
        # Resize uniquement pour le flux caméra (640x480 standard)
        return cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    except Exception as e:
        print(f"[camera] Erreur fetch : {e}")
        return None