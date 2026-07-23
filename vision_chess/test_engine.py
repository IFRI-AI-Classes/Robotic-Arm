import chess
from chess_engine.engine import ChessEngine
from chess_engine.validator import validate_move
from feedback.led import LEDController

def main():
    print("=== Test du Module Membre B (Moteur & LED) ===")
    
    led = LEDController()
    led.set_waiting()
    
    print("\n--- Test du Validator ---")
    board_before = chess.Board()
    board_after = board_before.copy()
    board_after.push_san("e4")
    
    move, status = validate_move(board_before, board_after)
    print(f"Validation du coup (attendu: e2e4, VALID) : {move}, {status}")
    if status == "VALID":
        led.set_valid()
    else:
        led.set_invalid()
        
    print("\n--- Test du Moteur d'échecs ---")
    print("Note: Assurez-vous d'avoir configuré STOCKFISH_PATH dans config.py")
    engine = ChessEngine()
    
    led.set_moving()
    best_move = engine.get_best_move(board_after)
    print(f"Le meilleur coup proposé par le moteur est : {best_move}")
    
    led.turn_off()
    engine.close()
    print("\nTests terminés.")

if __name__ == "__main__":
    main()
