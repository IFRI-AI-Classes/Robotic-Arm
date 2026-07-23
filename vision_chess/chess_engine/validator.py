import chess

def validate_move(board_before: chess.Board, board_after: chess.Board) -> tuple[chess.Move | None, str]:
    """
    Vérifie le coup que l'humain vient de jouer en comparant l'état du plateau 
    avant son action et l'état détecté par la caméra (YOLO) après son action.
    
    Args:
        board_before (chess.Board): L'état du plateau avant le coup de l'humain.
        board_after (chess.Board): L'état du plateau vu par la caméra après le coup.
        
    Returns:
        tuple[chess.Move | None, str]: 
            - Si un coup légal correspond : (Le Coup, "VALID")
            - Si plusieurs coups légaux correspondent (rare) : (None, "AMBIGUOUS")
            - Si aucun coup légal ne correspond : (None, "INVALID")
    """
    possible_moves = []
    
    # On itère sur tous les coups légaux que le joueur humain a le droit de faire
    for move in board_before.legal_moves:
        # On simule ce coup sur une copie de l'ancien plateau
        test_board = board_before.copy()
        test_board.push(move)
        
        # On compare la position des pièces du plateau simulé avec celle vue par la caméra.
        # "piece_map()" permet d'ignorer l'historique et de ne regarder que le placement pur.
        if test_board.piece_map() == board_after.piece_map():
            possible_moves.append(move)
            
    # Analyse des résultats de la simulation
    if len(possible_moves) == 1:
        # Parfait, un seul coup légal explique la nouvelle disposition
        return possible_moves[0], "VALID"
    elif len(possible_moves) > 1:
        # Ambiguïté. Arrive généralement lors d'une promotion si la caméra n'arrive 
        # pas à distinguer en quelle pièce le pion a été promu.
        return None, "AMBIGUOUS"
    else:
        # Le mouvement effectué par l'humain n'est pas permis par les règles des échecs,
        # ou l'IA de détection a fait une erreur de reconnaissance visuelle.
        return None, "INVALID"
