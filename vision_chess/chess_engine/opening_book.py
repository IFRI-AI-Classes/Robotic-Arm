import chess
import chess.polyglot
import os
import sys

# Ajout du dossier racine au système de chemin pour permettre l'importation de config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import POLYGLOT_PATH
except ImportError:
    POLYGLOT_PATH = ""

def get_opening_move(board: chess.Board) -> chess.Move | None:
    """
    Consulte la base d'ouvertures (fichier .bin Polyglot) pour trouver le meilleur coup.
    Cela évite d'utiliser le moteur Stockfish pour les premiers coups standards, ce qui 
    économise des ressources sur le Raspberry Pi.
    
    Args:
        board (chess.Board): L'état actuel du plateau d'échecs.
        
    Returns:
        chess.Move | None: Le coup recommandé par la base de données, ou None si 
                           le chemin n'est pas configuré, le fichier n'existe pas,
                           ou si la position actuelle n'est pas dans le livre.
    """
    # Vérification de l'existence du chemin vers la base Polyglot
    if not POLYGLOT_PATH or not os.path.exists(POLYGLOT_PATH):
        return None
        
    try:
        # Ouverture du fichier de base de données en mode lecture
        with chess.polyglot.open_reader(POLYGLOT_PATH) as reader:
            # Recherche de la position actuelle dans le livre
            entry = reader.find(board)
            if entry:
                return entry.move
    except IndexError:
        # La position n'a pas été trouvée dans le livre d'ouvertures
        return None
    except Exception as e:
        # Gestion des erreurs inattendues (ex: fichier corrompu)
        print(f"[Opening Book] Erreur lors de la lecture : {e}")
        return None
        
    return None
