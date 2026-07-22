import chess
from config import BOARD_SIZE


def build(full_state: dict) -> chess.Board:
    """
    Construit un chess.Board à partir de l'état complet des 64 cases.
    
    Args:
        full_state : dict {case: symbol | None}
                     symbol = lettre FEN ("P", "n", "K"...)
                     None   = case vide
    
    Returns:
        chess.Board peuplé (sans infos de tour ni de roque — juste les pièces)
    """
    board = chess.Board(fen=None)
    board.clear()

    for square_name, symbol in full_state.items():
        if symbol is None:
            continue
        try:
            square = chess.parse_square(square_name)
            piece  = chess.Piece.from_symbol(symbol)
            board.set_piece_at(square, piece)
        except Exception as e:
            print(f"[board_state] Erreur case {square_name} ({symbol}) : {e}")

    return board


def merge(board: chess.Board, detected: dict) -> chess.Board:
    """
    Met à jour un board existant avec les cases modifiées détectées.
    Plus fiable que rebuild complet — évite les erreurs YOLO sur les cases non touchées.
    
    Args:
        board    : chess.Board courant (état avant le coup)
        detected : dict {case: symbol | None} — uniquement les cases modifiées
    
    Returns:
        chess.Board mis à jour
    """
    updated = board.copy()
    for square_name, symbol in detected.items():
        try:
            square = chess.parse_square(square_name)
            if symbol is None:
                updated.remove_piece_at(square)
            else:
                updated.set_piece_at(square, chess.Piece.from_symbol(symbol))
        except Exception as e:
            print(f"[board_state] Erreur merge {square_name} : {e}")
    return updated


def to_fen(board: chess.Board) -> str:
    """Retourne la partie pièces du FEN (sans tour/roque/en passant)."""
    return board.board_fen()