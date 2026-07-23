import cv2
import numpy as np
from ultralytics import YOLO
from config import YOLO_MODEL_PATH

CLASS_MAP = {
    "white-pawn":   "P", "white-knight": "N", "white-bishop": "B",
    "white-rook":   "R", "white-queen":  "Q", "white-king":   "K",
    "black-pawn":   "p", "black-knight": "n", "black-bishop": "b",
    "black-rook":   "r", "black-queen":  "q", "black-king":   "k",
    "bishop":       "b",
}

_model = None

def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(YOLO_MODEL_PATH)
    return _model


def run(warped: np.ndarray, squares: dict, changed: list[str] | None = None) -> dict:
    """
    Détecte les pièces en passant le plateau entier à YOLO.
    Mappe chaque bounding box à la case correspondante via ses coordonnées.

    Args:
        warped  : vue redressée 800x800 issue de board_detector.detect()
        squares : dict {case: ROI} — sert uniquement à connaître les cases valides
        changed : si fourni, retourne uniquement ces cases — sinon retourne les 64

    Returns:
        dict {case: symbol | None}
        symbol = lettre FEN ("P", "n"...), None = case vide
    """
    model = _get_model()
    results = {sq: None for sq in squares.keys()}

    # Redimensionner le plateau entier pour YOLO
    img = cv2.resize(warped, (416, 416))
    sq_size = 416 / 8  # taille d'une case dans l'espace 416x416 = 52px

    detections = model(img, verbose=False, conf=0.3)
    boxes = detections[0].boxes

    if boxes is None or len(boxes) == 0:
        return {sq: results[sq] for sq in (changed or squares.keys())}

    best_conf = {}  # {case: conf} pour garder la meilleure détection par case

    for i in range(len(boxes)):
        x_center = boxes.xywh[i][0].item()
        y_center = boxes.xywh[i][1].item()
        conf     = boxes.conf[i].item()

        col = int(x_center // sq_size)
        row = int(y_center // sq_size)
        col = max(0, min(7, col))
        row = max(0, min(7, row))

        file        = chr(ord('a') + col)
        rank        = str(8 - row)
        square_name = f"{file}{rank}"

        # Garder uniquement la détection avec la meilleure confiance par case
        if conf > best_conf.get(square_name, 0):
            class_id   = int(boxes.cls[i].item())
            class_name = detections[0].names[class_id]
            results[square_name] = CLASS_MAP.get(class_name)
            best_conf[square_name] = conf

    if changed is not None:
        return {sq: results.get(sq) for sq in changed}

    return results