import cv2
import chess
from perception.camera import fetch_frame
from perception.stability import StabilityDetector
from perception.board_detector import detect, draw_grid
from perception.diff import get_changed_squares
from chess_engine.engine import ChessEngine
from chess_engine.validator import validate_move
from feedback.led import LEDController

stability = StabilityDetector()
snapshot_before: dict | None = None
internal_board = chess.Board()
engine = ChessEngine()
led = LEDController()
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
        internal_board = board.copy() # Synchronisation avec la détection
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
            
            # --- Phase 3 & 4 (Membre B) ---
            move, status = validate_move(internal_board, board)
            if status == "VALID":
                print(f"[main] Coup validé : {move}")
                led.set_valid()
                internal_board.push(move) # Maj du plateau interne
                board = internal_board.copy() # On resynchronise la vision sur la réalité validée
                
                # Calcul de la réponse de l'IA
                led.set_moving()
                best_move = engine.get_best_move(internal_board)
                if best_move:
                    print(f"[main] Stockfish a choisi : {best_move}")
                    internal_board.push(best_move)
                    board = internal_board.copy() # On resynchronise pour l'affichage
                    
                    # TODO: Phase 6/7 -> UART et Cinématique inverse vers le bras
                    print(f"[main] -> Envoi de la commande {best_move} au bras robotique...")
                
                led.set_waiting()
            else:
                print(f"[main] Coup INVALIDE ou ambigu ({status}). Veuillez corriger le plateau.")
                led.set_invalid()
                board = internal_board.copy() # On annule la fausse détection dans la vision

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