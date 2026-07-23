# ============================================================
#  CONFIG — vision_chess
# ============================================================

# --- Caméra ---
CAMERA_URL = "http://192.168.48.176:8080/shot.jpg"  # IP Webcam
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# ---Image pour les test ou l'entraînement
TEST_MODE       = True
TEST_IMAGE_PATH = r"D:\Web-projects\bras_robotique\test\images.jpg"

# --- Plateau ---
INNER_CORNERS = (7, 7)   # coins intérieurs échiquier 8x8
                          # mettre (4, 4) pour ta grille 5x5 de test
BOARD_SIZE = 800          # taille en px de la vue redressée (carré)

# --- Padding (étendre au-delà des coins intérieurs détectés) ---
# 1.0 = exactement les coins intérieurs, >1.0 = on étend vers les bords
BOARD_PADDING = 1.0      # augmenter si les bords sont coupés (ex: 1.15)

# --- Stabilité ---
STABILITY_THRESHOLD = 15  # diff moyen max entre frames pour dire "stable"
STABILITY_FRAMES    = 8   # nb de frames stables consécutives requises

# --- Diff ---
DIFF_THRESHOLD = 20       # diff moyen par case pour dire "case modifiée"

# --- YOLO ---
YOLO_MODEL_PATH = r"vision_chess\assets\best.pt"

# ============================================================
#  CONFIG — chess_engine & feedback (Phase 3 & 4)
# ============================================================

STOCKFISH_PATH = r"stockfish" 
ENGINE_SKILL_LEVEL = 10     
ENGINE_MOVE_TIME = 1000     

POLYGLOT_PATH = "" 
SYZYGY_PATH = "" 

LED_COUNT      = 1          
LED_PIN        = 18         
LED_FREQ_HZ    = 800000     
LED_DMA        = 10         
LED_BRIGHTNESS = 255        
LED_INVERT     = False      
LED_CHANNEL    = 0          
