import chess
import chess.engine
import os
import sys

from .opening_book import get_opening_move
from .tablebase import get_tablebase_move

# Ajout du dossier racine au système de chemin pour l'import de config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import STOCKFISH_PATH, ENGINE_SKILL_LEVEL, ENGINE_MOVE_TIME
except ImportError:
    # Valeurs par défaut en cas d'absence de config.py
    STOCKFISH_PATH = "stockfish"
    ENGINE_SKILL_LEVEL = 10
    ENGINE_MOVE_TIME = 1000

class ChessEngine:
    """
    Classe principale gérant la prise de décision du robot.
    Elle orchestre l'utilisation de la base d'ouvertures, des tablebases de finales,
    et du moteur Stockfish pour calculer le meilleur coup à jouer.
    """
    def __init__(self):
        self.engine = None
        self._init_engine()
        
    def _init_engine(self):
        """Initialise la communication avec l'exécutable externe Stockfish."""
        try:
            # Lance le processus Stockfish via le protocole UCI (Universal Chess Interface)
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            # Règle la difficulté du robot selon la configuration
            self.engine.configure({"Skill Level": ENGINE_SKILL_LEVEL})
            print("[ChessEngine] Moteur Stockfish chargé avec succès.")
        except Exception as e:
            print(f"[ChessEngine] Attention, impossible de charger Stockfish. Vérifiez le STOCKFISH_PATH dans config.py. Erreur : {e}")
            
    def get_best_move(self, board: chess.Board) -> chess.Move | None:
        """
        Détermine le meilleur coup à jouer dans la position donnée.
        L'algorithme suit un ordre de priorité pour économiser le CPU du Raspberry Pi :
        1. Base d'ouvertures (Polyglot)
        2. Finales pré-calculées (Syzygy)
        3. Calcul pur (Stockfish)
        """
        # 1. Vérification dans la base d'ouvertures
        move = get_opening_move(board)
        if move:
            print(f"[ChessEngine] Coup d'ouverture trouvé : {move}")
            return move
            
        # 2. Vérification dans les tablebases de finales (s'il reste peu de pièces)
        move = get_tablebase_move(board)
        if move:
            print(f"[ChessEngine] Coup de finale (Syzygy) trouvé : {move}")
            return move
            
        # 3. Appel au moteur Stockfish si aucune des méthodes rapides n'a fonctionné
        if self.engine is None:
            print("[ChessEngine] Moteur non disponible !")
            return None
            
        try:
            # Définition de la limite de temps de réflexion (convertie en secondes)
            limit = chess.engine.Limit(time=ENGINE_MOVE_TIME / 1000.0)
            
            # Stockfish analyse la position et renvoie le meilleur coup trouvé
            result = self.engine.play(board, limit)
            print(f"[ChessEngine] Coup Stockfish calculé : {result.move}")
            return result.move
        except Exception as e:
            print(f"[ChessEngine] Erreur lors du calcul : {e}")
            return None
            
    def close(self):
        """Termine le processus Stockfish proprement. À appeler en fin de programme."""
        if self.engine:
            self.engine.quit()
