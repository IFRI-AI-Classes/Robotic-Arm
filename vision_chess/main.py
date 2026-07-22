import cv2
import chess
from perception.camera import fetch_frame
from perception.stability import StabilityDetector
from perception.board_detector import detect, draw_grid
from perception.diff import get_changed_squares
from detection.piece_detector import run as detect_pieces
from detection.board_state import build, merge, to_fen

stability        = StabilityDetector()
snapshot_squares: dict | None  = None
board: chess.Board | None      = None
STATE = "INIT"

while True:
    frame = fetch_frame()
    if frame is None:
        continue

    stable = stability.update(frame)
    if not stable:
        cv2.imshow("vision_chess", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    warped, squares, H = detect(frame)
    cv2.imshow("warped", warped)
    if warped is None:
        cv2.putText(frame, "PLATEAU NON DETECTE", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.imshow("vision_chess", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # ---- INIT ----
    if STATE == "INIT":
        print("[main] Analyse initiale du plateau...")
        full_detection = detect_pieces(warped, squares, changed=None)
        board = build(full_detection)
        snapshot_squares = squares
        print(f"[main] Board initial :\n{board}")
        print(f"[main] FEN : {to_fen(board)}")
        STATE = "WAIT_PLAYER"

    # ---- WAIT_PLAYER ----
    elif STATE == "WAIT_PLAYER":
        changed = get_changed_squares(snapshot_squares, squares)

        if changed:
            print(f"[main] Cases modifiées : {changed}")
            partial_detection = detect_pieces(warped, squares, changed=changed)
            print(f"[main] Détections : {partial_detection}")
            board = merge(board, partial_detection)
            snapshot_squares = squares
            print(f"[main] Board après coup :\n{board}")
            print(f"[main] FEN : {to_fen(board)}")
            # → chess_engine/validator.py ici

    # ---- Affichage ----
    display = draw_grid(warped)
    cv2.putText(display, f"STATE: {STATE}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    if board:
        cv2.putText(display, f"FEN: {to_fen(board)[:40]}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    cv2.imshow("vision_chess", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()