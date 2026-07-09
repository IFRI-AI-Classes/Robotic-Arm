# Module perception

Responsable de tout ce qui concerne la caméra et l'analyse de l'image brute.
Ce module ne fait pas de classification — il prépare les données pour `detection/`.

## Fichiers

| Fichier | Rôle | Input | Output |
|---|---|---|---|
| `camera.py` | Récupère les frames | — | `np.ndarray` BGR |
| `stability.py` | Détecte si le plateau est immobile | frame BGR | `bool` |
| `board_detector.py` | Homographie + découpe 64 cases | frame BGR | `warped`, `squares`, `H` |
| `diff.py` | Compare deux états du plateau | 2x dict squares | `list[str]` cases modifiées |

---

## Utilisation dans main.py

Ordre strict à respecter — chaque étape dépend de la précédente.

```python
from perception.camera import fetch_frame
from perception.stability import StabilityDetector
from perception.board_detector import detect, draw_grid
from perception.diff import get_changed_squares

stability = StabilityDetector()
snapshot_before = None

while True:
    # 1. Récupérer une frame
    frame = fetch_frame()
    if frame is None:
        continue

    # 2. Vérifier la stabilité — ne pas analyser si le plateau bouge
    if not stability.update(frame):
        continue

    # 3. Détecter le plateau et obtenir les 64 cases
    warped, squares, H = detect(frame)
    if warped is None:
        continue  # plateau absent ou mal cadré

    # 4. Prendre le snapshot initial
    if snapshot_before is None:
        snapshot_before = squares
        continue

    # 5. Détecter les cases qui ont changé depuis le dernier snapshot
    changed = get_changed_squares(snapshot_before, squares)
    if changed:
        print(f"Cases modifiées : {changed}")
        # → transmettre (warped, squares, changed) à detection/
        snapshot_before = squares
```

---

## Configuration (config.py)

| Paramètre | Défaut | Description |
|---|---|---|
| `TEST_MODE` | `True` | Charge une image fixe au lieu de la caméra IP |
| `TEST_IMAGE_PATH` | `"plateau.jpg"` | Chemin de l'image de test |
| `CAMERA_URL` | — | URL IP Webcam (prod) |
| `INNER_CORNERS` | `(7, 7)` | Coins intérieurs pour un échiquier 8x8 |
| `BOARD_SIZE` | `800` | Taille en px de la vue redressée |
| `BOARD_PADDING` | `1.0` | Étendre les bords si les cases sont coupées (essayer 1.1–1.2) |
| `STABILITY_THRESHOLD` | `15` | Diff max entre frames pour dire "stable" |
| `STABILITY_FRAMES` | `8` | Nb de frames stables consécutives requises |
| `DIFF_THRESHOLD` | `20` | Diff moyen par case pour dire "case modifiée" |

---

## Utilisation pour l'entraînement YOLO

Le module permet de collecter automatiquement les ROIs des 64 cases
pour constituer le dataset d'entraînement.

### 1. Collecter les images

Ajouter dans `board_detector.py` la fonction suivante :

```python
import os

def save_rois(squares: dict, output_dir: str, prefix: str = ""):
    """
    Sauvegarde les ROIs des 64 cases dans output_dir.
    Appeler après detect() pour chaque position à annoter.
    
    Structure générée :
        output_dir/
            a1_0001.jpg
            a2_0001.jpg
            ...
    """
    os.makedirs(output_dir, exist_ok=True)
    existing = len(os.listdir(output_dir))
    for square, roi in squares.items():
        filename = f"{square}_{prefix or str(existing).zfill(4)}.jpg"
        cv2.imwrite(os.path.join(output_dir, filename), roi)
```

Appeler dans `main.py` après `detect()` pour chaque position à capturer :

```python
from perception.board_detector import detect, save_rois

warped, squares, H = detect(frame)
if squares:
    save_rois(squares, output_dir="dataset/raw", prefix="pos001")
```

### 2. Annoter

Importer le dossier `dataset/raw/` dans **Roboflow** ou **LabelImg**.
Créer une classe par type de pièce + une classe `empty` :

```
white_pawn, white_knight, white_bishop, white_rook, white_queen, white_king
black_pawn, black_knight, black_bishop, black_rook, black_queen, black_king
empty
```

Exporter au format **YOLOv8** (`.yaml` + dossiers `images/` et `labels/`).

### 3. Entraîner

```bash
yolo train data=dataset/data.yaml model=yolov8n.pt epochs=50 imgsz=100
```

`imgsz=100` correspond à la taille d'une case (BOARD_SIZE // 8 = 100px pour 800px).
Le modèle entraîné (`best.pt`) va dans `assets/` et son chemin est déclaré
dans `config.py` sous `YOLO_MODEL_PATH`.

### 4. Tester la détection sur une case

```python
from ultralytics import YOLO
import cv2

model = YOLO("assets/best.pt")
roi = squares["e4"]  # ROI issue de detect()
results = model(roi)
print(results[0].names[results[0].probs.top1])  # classe prédite
```

---

## Points d'attention

- Ne jamais appeler `detect()` sans avoir vérifié la stabilité avant —
  une frame floue ou en mouvement produit une homographie incorrecte
- `BOARD_PADDING` à ajuster selon le cadre physique du plateau :
  augmenter si les bords sont coupés, réduire si les coins
  débordent
- En prod (caméra IP), tester d'abord `TEST_MODE = True` avec une photo du plateau réel avant de basculer sur le flux live.