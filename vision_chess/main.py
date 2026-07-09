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

    display = draw_grid(warped)
    cv2.putText(display, "STABLE - PLATEAU DETECTE", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("vision_chess", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()