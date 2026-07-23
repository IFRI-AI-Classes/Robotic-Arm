import cv2
from perception.camera import fetch_frame
from perception.stability import StabilityDetector
from perception.board_detector import detect, draw_grid
from perception.diff import get_changed_squares

stability = StabilityDetector()
snapshot_before: dict | None = None

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

    if warped is None:
        cv2.putText(frame, "PLATEAU NON DETECTE", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.imshow("vision_chess", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    if snapshot_before is None:
        snapshot_before = squares
        print("[main] Snapshot initial pris.")

    changed = get_changed_squares(snapshot_before, squares)
    if changed:
        print(f"[main] Cases modifiées : {changed}")
        snapshot_before = squares
        
        # --- Phase 2: MOCK YOLO ---
        # Membre A n'a pas encore fait la détection YOLO.
        # On génère un 'board_after' mocké (ex: le joueur a joué le premier coup légal possible)
        board_after = internal_board.copy()
        legal_moves = list(internal_board.legal_moves)
        if not legal_moves:
            print("Fin de partie.")
            led.turn_off()
            break
            
        # Mock d'un coup humain
        simulated_human_move = legal_moves[0]
        board_after.push(simulated_human_move)
        print(f"[MOCK YOLO] Le joueur humain a joué (simulé) : {simulated_human_move}")

        # --- Phase 3 & 4 (Membre B) ---
        move, status = validate_move(internal_board, board_after)
        if status == "VALID":
            print(f"[main] Coup validé : {move}")
            led.set_valid()
            internal_board.push(move) # Maj du plateau interne
            
            # Calcul de la réponse de l'IA
            led.set_moving()
            best_move = engine.get_best_move(internal_board)
            if best_move:
                print(f"[main] Stockfish a choisi : {best_move}")
                internal_board.push(best_move)
                
                # TODO: Phase 6/7 -> UART et Cinématique inverse vers le bras
                print(f"[main] -> Envoi de la commande {best_move} au bras robotique...")
            
            led.set_waiting()
        else:
            print(f"[main] Coup INVALIDE ou ambigu ({status}). Veuillez corriger le plateau.")
            led.set_invalid()

    display = draw_grid(warped)
    cv2.putText(display, "STABLE - PLATEAU DETECTE", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("vision_chess", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()