import cv2
import numpy as np
from config import INNER_CORNERS, BOARD_SIZE, BOARD_PADDING


def detect(frame: np.ndarray) -> tuple[np.ndarray | None, dict | None, np.ndarray | None]:
    """
    Détecte le plateau, applique l'homographie, découpe les 64 cases.
    Retourne (warped, squares, H) ou (None, None, None) si non détecté.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCornersSB(gray, INNER_CORNERS, None)

    if not found:
        print("[board_detector] Plateau non détecté.")
        return None, None, None

    corners = cv2.cornerSubPix(
        gray, corners, (11, 11), (-1, -1),
        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    )

    # Coins extrêmes des coins intérieurs détectés
    n = INNER_CORNERS[0]
    tl = corners[0][0].tolist()
    tr = corners[n - 1][0].tolist()
    bl = corners[n * (n - 1)][0].tolist()
    br = corners[n * n - 1][0].tolist()

    # Taille estimée d'une case
    sq_w = (tr[0] - tl[0]) / (n - 1)
    sq_h = (bl[1] - tl[1]) / (n - 1)

    # Étendre d'une case dans chaque direction pour inclure les bords du plateau
    pad_w = sq_w * BOARD_PADDING
    pad_h = sq_h * BOARD_PADDING

    tl = [tl[0] - pad_w, tl[1] - pad_h]
    tr = [tr[0] + pad_w, tr[1] - pad_h]
    bl = [bl[0] - pad_w, bl[1] + pad_h]
    br = [br[0] + pad_w, br[1] + pad_h]

    src = np.float32([tl, tr, bl, br])
    dst = np.float32([
        [0, 0],
        [BOARD_SIZE, 0],
        [0, BOARD_SIZE],
        [BOARD_SIZE, BOARD_SIZE]
    ])

    H, _ = cv2.findHomography(src, dst)
    warped = cv2.warpPerspective(frame, H, (BOARD_SIZE, BOARD_SIZE))
    squares = _extract_squares(warped)

    return warped, squares, H


def _extract_squares(warped: np.ndarray) -> dict:
    """Découpe la vue redressée en 64 cases nommées."""
    sq = BOARD_SIZE // 8
    squares = {}
    for row in range(8):
        for col in range(8):
            x1, y1 = col * sq, row * sq
            roi = warped[y1:y1 + sq, x1:x1 + sq]
            file = chr(ord('a') + col)
            rank = str(8 - row)
            squares[f"{file}{rank}"] = roi
    return squares


def draw_grid(warped: np.ndarray) -> np.ndarray:
    """Affiche la grille sur la vue redressée — utile pour debug."""
    display = warped.copy()
    sq = BOARD_SIZE // 8
    for i in range(9):
        cv2.line(display, (i * sq, 0), (i * sq, BOARD_SIZE), (0, 255, 0), 1)
        cv2.line(display, (0, i * sq), (BOARD_SIZE, i * sq), (0, 255, 0), 1)
    for row in range(8):
        for col in range(8):
            label = f"{chr(ord('a') + col)}{8 - row}"
            cv2.putText(display, label, (col * sq + 4, row * sq + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    return display