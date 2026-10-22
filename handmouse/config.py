"""Configurações do HandMouse. Ajuste os valores aqui para calibrar o controle."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# --- Câmera ---
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MIRROR = True  # espelha a imagem para o movimento parecer natural

# --- Detecção da mão (MediaPipe) ---
MODEL_PATH = ROOT_DIR / "models" / "hand_landmarker.task"
NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.6
MIN_PRESENCE_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# --- Controle do mouse ---
# False = apenas mostra a mão e o gesto na janela (Etapa 1), sem mexer no mouse
MOUSE_ENABLED = True

# Ponto da mão que guia o cursor (8 = ponta do indicador)
CURSOR_LANDMARK = 8

# Área útil da câmera, em coordenadas normalizadas (0 a 1): x_min, y_min, x_max, y_max.
# Uma área menor que o quadro inteiro permite alcançar as bordas da tela sem esticar o braço.
ACTIVE_AREA = (0.20, 0.15, 0.80, 0.65)

# Suavização: quanto maior, mais estável e mais lento o cursor (1 = sem suavização)
SMOOTHING = 5.0

# --- Gestos ---
# Pinça: distância polegar-indicador dividida pelo tamanho da mão.
# Dois limiares (histerese) evitam que a pinça "pisque" perto do limite.
PINCH_ON_THRESHOLD = 0.35
PINCH_OFF_THRESHOLD = 0.45

# Palma aberta só conta com o polegar bem longe do indicador, para não confundir com a pinça
PAUSE_MIN_PINCH_RATIO = 0.6

# Quantos frames seguidos um gesto precisa aparecer para ser aceito
STABLE_FRAMES = 3

# Pinça mantida por mais que isso (segundos) vira arrasto em vez de clique
DRAG_HOLD_TIME = 0.4

# Intervalo mínimo entre cliques (segundos)
CLICK_COOLDOWN = 0.3

# Ao fazer a pinça o indicador desce junto; o cursor volta para onde estava esse tempo antes
CLICK_ROLLBACK_TIME = 0.3

# Palma aberta mantida por esse tempo (segundos) pausa ou retoma o controle
PAUSE_HOLD_TIME = 1.0

# --- Teclas de atalho globais (funcionam mesmo fora da janela, só no Windows) ---
# Códigos de tecla virtual do Windows: 0x77 = F8, 0x79 = F10
HOTKEY_TOGGLE_PAUSE = 0x77
HOTKEY_EXIT = 0x79

# --- Janela ---
WINDOW_NAME = "HandMouse"
SHOW_WINDOW = True

# Imprime no terminal a medida da pinça e os dedos detectados, para calibrar
DEBUG = True
