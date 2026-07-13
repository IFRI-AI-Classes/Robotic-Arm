# Module chess_engine

Responsable de toute la logique décisionnelle du jeu d'échecs. Ce module (développé par le Membre B) prend en entrée l'état du plateau détecté par la vision et détermine le meilleur coup à jouer pour le bras robotique.

## Fichiers

| Fichier | Rôle | Input | Output |
|---|---|---|---|
| `validator.py` | Vérifie que le coup joué par l'humain est légal | `board_before`, `board_after` | `chess.Move` (ou statut d'erreur) |
| `opening_book.py` | Joue les ouvertures instantanément | `chess.Board` | `chess.Move` (ou None) |
| `tablebase.py` | Résout les finales parfaitement (≤ 4 pièces) | `chess.Board` | `chess.Move` (ou None) |
| `engine.py` | Moteur central appelant Stockfish | `chess.Board` | `chess.Move` |

---

## Utilisation dans main.py

Le module est conçu pour être utilisé une fois que le plateau s'est stabilisé et que la détection visuelle a été transformée en objet `chess.Board`.

```python
from chess_engine.engine import ChessEngine
from chess_engine.validator import validate_move
import chess

# Initialisation du moteur (à faire une seule fois au début)
engine = ChessEngine()

# 1. Valider le coup de l'humain
# board_before = l'état interne avant que l'humain ne bouge
# board_after = l'état détecté par YOLO
move, status = validate_move(board_before, board_after)

if status == "VALID":
    print(f"L'humain a joué : {move}")
    # On met à jour l'état officiel
    board_before.push(move)
    
    # 2. Faire réfléchir le robot
    best_move = engine.get_best_move(board_before)
    print(f"Le robot doit jouer : {best_move}")
    
    # 3. Envoyer 'best_move' à l'ESP32 via UART pour bouger le bras...
else:
    print(f"Erreur : {status} (Mouvement illégal ou erreur caméra)")

# En fin de programme
engine.close()
```

---

## Configuration (config.py)

| Paramètre | Défaut | Description |
|---|---|---|
| `STOCKFISH_PATH` | `"stockfish"` | Chemin absolu vers l'exécutable Stockfish (.exe sous Windows). |
| `ENGINE_SKILL_LEVEL` | `10` | Niveau de difficulté du robot (0 à 20). |
| `ENGINE_MOVE_TIME` | `1000` | Temps de calcul maximum par coup (en millisecondes). |
| `POLYGLOT_PATH` | `""` | Chemin vers le fichier `.bin` des ouvertures (optionnel). |
| `SYZYGY_PATH` | `""` | Chemin vers le dossier des tablebases de finales (optionnel). |

---

## Installation de Stockfish

Contrairement aux autres paquets Python, Stockfish est un exécutable autonome (C++).

### Sous Windows (Développement)
1. Téléchargez Stockfish depuis [stockfishchess.org](https://stockfishchess.org/download/).
2. Extrayez le fichier `.exe`.
3. Mettez le chemin complet vers cet `.exe` dans `config.py` sous `STOCKFISH_PATH`.

### Sous Raspberry Pi (Production)
1. Installez-le via le terminal : `sudo apt install stockfish`
2. Mettez `STOCKFISH_PATH = "/usr/games/stockfish"` dans `config.py`.

---

## Points d'attention

- **Gestion des ressources** : Ne lancez jamais `engine.get_best_move()` en même temps qu'une inférence YOLO lourde. Dans la boucle principale, la caméra doit se mettre en pause pendant que Stockfish calcule pour éviter de saturer le processeur du Raspberry Pi.
- **Fermeture** : N'oubliez pas d'appeler `engine.close()` quand le programme se termine pour ne pas laisser des processus Stockfish "zombies" tourner en arrière-plan.
