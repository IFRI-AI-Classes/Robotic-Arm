import chess
import chess.syzygy
import os
import sys

# Ajout du dossier racine au système de chemin pour permettre l'importation de config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import SYZYGY_PATH
except ImportError:
    SYZYGY_PATH = ""

def get_tablebase_move(board: chess.Board) -> chess.Move | None:
    """
    Consulte les tablebases Syzygy pour jouer parfaitement les fins de partie.
    Cette fonction n'est activée que s'il reste 4 pièces ou moins sur le plateau.
    
    Args:
        board (chess.Board): L'état actuel du plateau d'échecs.
        
    Returns:
        chess.Move | None: Le meilleur coup garantissant le meilleur résultat (gain, nul, 
                           ou résistance maximale), ou None si la position ne peut 
                           pas être évaluée.
    """
    # Vérification de l'existence du dossier contenant les tablebases
    if not SYZYGY_PATH or not os.path.isdir(SYZYGY_PATH):
        return None
        
    # Limite matérielle : Les tablebases Syzygy nécessitent énormément d'espace disque.
    # On se limite ici à 4 pièces maximum pour rester léger sur le Raspberry Pi.
    if len(board.piece_map()) > 4:
        return None
        
    try:
        # Ouverture des tablebases
        with chess.syzygy.open_tablebase(SYZYGY_PATH) as tablebase:
            best_move = None
            best_score = -99999
            
            # Évaluation de tous les coups légaux disponibles
            for move in board.legal_moves:
                # On simule le coup sur le plateau
                board.push(move)
                try:
                    # 'probe_wdl' donne le score (Win, Draw, Loss) après ce coup.
                    # Le score renvoyé est du point de vue de l'adversaire (qui doit jouer
                    # après notre coup simulé). On l'inverse (-) pour l'avoir de notre point de vue.
                    wdl = -tablebase.probe_wdl(board)
                    
                    # Si ce coup mène à un meilleur résultat, on le mémorise
                    if wdl > best_score:
                        best_score = wdl
                        best_move = move
                except chess.syzygy.MissingTableError:
                    # La tablebase spécifique pour ce groupe de pièces n'est pas installée
                    pass
                finally:
                    # On annule le coup simulé pour revenir à l'état initial
                    board.pop()
                    
            return best_move
    except Exception as e:
        print(f"[Tablebase] Erreur d'accès aux tablebases : {e}")
        return None
