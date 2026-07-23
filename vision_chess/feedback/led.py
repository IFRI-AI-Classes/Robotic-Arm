import sys
import os

# Ajout du dossier racine au système de chemin pour l'import de config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
except ImportError:
    # Valeurs par défaut si le fichier config.py est inaccessible
    LED_COUNT = 1
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 255
    LED_INVERT = False
    LED_CHANNEL = 0

# Tentative d'importation de la librairie matérielle du Raspberry Pi
try:
    from rpi_ws281x import PixelStrip, Color
    HAS_HW = True
except ImportError:
    # Si on est sur Windows, l'import échoue. On active alors le mode Simulation (Mock).
    HAS_HW = False
    
class LEDController:
    """
    Contrôleur gérant le retour d'information visuel (LED) pour l'utilisateur.
    Utilise la vraie LED sur Raspberry Pi, ou la console système sous Windows.
    """
    
    # Définition des codes couleurs (Rouge, Vert, Bleu)
    WAITING = (255, 255, 0)  # Jaune : En attente d'une action
    VALID   = (0, 255, 0)    # Vert  : Le coup humain a été validé
    INVALID = (255, 0, 0)    # Rouge : Le coup humain est illégal ou erreur caméra
    MOVING  = (0, 0, 255)    # Bleu  : Le bras robotique est en mouvement
    END     = (255, 255, 255)# Blanc : Fin de la partie (Mat/Pat)
    OFF     = (0, 0, 0)      # Éteint
    
    def __init__(self):
        self.has_hw = HAS_HW
        if self.has_hw:
            # Configuration matérielle du ruban LED/NeoPixel
            self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
            self.strip.begin()
            print("[LED] Matériel détecté et initialisé.")
        else:
            print("[LED] Mode MOCK (Windows) : Simulation d'affichage dans la console.")
            
    def _color_to_name(self, r, g, b):
        """Traduit une couleur RGB en nom lisible pour le mode MOCK."""
        if (r, g, b) == self.WAITING: return "JAUNE (En attente)"
        if (r, g, b) == self.VALID:   return "VERT (Coup valide)"
        if (r, g, b) == self.INVALID: return "ROUGE (Erreur/Invalide)"
        if (r, g, b) == self.MOVING:  return "BLEU (Mouvement bras)"
        if (r, g, b) == self.END:     return "BLANC (Fin partie)"
        if (r, g, b) == self.OFF:     return "ÉTEINT"
        return f"RGB({r},{g},{b})"

    def set_color(self, color):
        """Applique une couleur spécifique à la LED (ou l'affiche en console)."""
        if self.has_hw:
            # La librairie Color utilise souvent G,R,B ou R,G,B selon le matériel.
            # Ici on convertit le tuple en objet Color compréhensible par la librairie.
            c = Color(color[0], color[1], color[2])
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, c)
            self.strip.show()
        else:
            # Mode MOCK : on affiche juste ce qui se passerait
            name = self._color_to_name(*color)
            print(f"[LED-MOCK] Changement d'état : {name}")
            
    # Méthodes d'aide pour changer rapidement l'état du système
    def set_waiting(self): self.set_color(self.WAITING)
    def set_valid(self):   self.set_color(self.VALID)
    def set_invalid(self): self.set_color(self.INVALID)
    def set_moving(self):  self.set_color(self.MOVING)
    def set_end(self):     self.set_color(self.END)
    def turn_off(self):    self.set_color(self.OFF)
