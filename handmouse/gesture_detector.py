"""Interpretação dos gestos a partir dos 21 pontos da mão."""

from enum import Enum

import numpy as np

from handmouse import config

# Índices dos pontos do MediaPipe
WRIST = 0
THUMB_IP, THUMB_TIP = 3, 4
INDEX_MCP = 5
MIDDLE_MCP = 9
PINKY_MCP = 17
# (ponta, articulação do meio) de indicador, médio, anelar e mínimo
FINGERS = [(8, 6), (12, 10), (16, 14), (20, 18)]


class Gesture(Enum):
    NONE = "nenhum"
    MOVE = "mover"
    PINCH = "pinca"
    RIGHT_CLICK = "clique direito"
    PAUSE = "pausa"


# Os pontos vêm normalizados de 0 a 1 nos dois eixos; corrige x para a proporção real da imagem
ASPECT = config.FRAME_WIDTH / config.FRAME_HEIGHT


def _dist(a, b):
    return float(np.hypot((a[0] - b[0]) * ASPECT, a[1] - b[1]))


def fingers_up(lm):
    """Retorna [polegar, indicador, médio, anelar, mínimo] como booleanos.

    Compara distâncias em vez de coordenadas y, assim funciona com a mão inclinada.
    """
    thumb = _dist(lm[THUMB_TIP], lm[PINKY_MCP]) > _dist(lm[THUMB_IP], lm[PINKY_MCP])
    others = [_dist(lm[tip], lm[WRIST]) > _dist(lm[pip], lm[WRIST]) for tip, pip in FINGERS]
    return [thumb] + others


def pinch_ratio(lm):
    """Distância polegar-indicador dividida pelo tamanho da mão (pulso até a base do médio)."""
    hand_size = _dist(lm[WRIST], lm[MIDDLE_MCP])
    if hand_size == 0:
        return float("inf")
    return _dist(lm[THUMB_TIP], lm[8]) / hand_size


class GestureDetector:
    def __init__(self, stable_frames=config.STABLE_FRAMES):
        self.stable_frames = stable_frames
        self.pinching = False
        self.current = Gesture.NONE
        self._candidate = Gesture.NONE
        self._count = 0
        # Últimas medidas, para exibir na tela durante a calibração
        self.last_ratio = None
        self.last_fingers = None

    def _raw_gesture(self, lm):
        ratio = pinch_ratio(lm)
        fingers = fingers_up(lm)
        self.last_ratio, self.last_fingers = ratio, fingers

        threshold = config.PINCH_OFF_THRESHOLD if self.pinching else config.PINCH_ON_THRESHOLD
        self.pinching = ratio < threshold
        if self.pinching:
            return Gesture.PINCH

        thumb, index, middle, ring, pinky = fingers
        if all(fingers) and ratio > config.PAUSE_MIN_PINCH_RATIO:
            return Gesture.PAUSE
        if index and middle and not ring and not pinky:
            return Gesture.RIGHT_CLICK
        if index and not middle and not ring and not pinky:
            return Gesture.MOVE
        return Gesture.NONE

    def update(self, landmarks):
        """Recebe os pontos do frame (ou None) e retorna o gesto estabilizado."""
        raw = Gesture.NONE if landmarks is None else self._raw_gesture(landmarks)
        if landmarks is None:
            self.pinching = False
            self.last_ratio = self.last_fingers = None

        # Só troca de gesto depois de vê-lo em vários frames seguidos
        if raw == self._candidate:
            self._count += 1
        else:
            self._candidate = raw
            self._count = 1
        if self._count >= self.stable_frames:
            self.current = self._candidate
        return self.current
