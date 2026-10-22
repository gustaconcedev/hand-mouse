"""Converte gestos e posições da mão em movimento do cursor, cliques e arrasto."""

import time
from collections import deque

import numpy as np
import pyautogui

from handmouse import config
from handmouse.gesture_detector import Gesture

pyautogui.PAUSE = 0  # o padrão de 0,1 s por comando deixaria o cursor travado
pyautogui.FAILSAFE = True  # levar o mouse físico a um canto da tela encerra o programa


class MouseController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.pos = None  # posição suavizada do cursor
        self.history = deque(maxlen=120)  # (tempo, posição) recentes, para desfazer a descida da pinça
        self.drag_offset = np.zeros(2)  # compensa o dedo abaixado durante o arrasto
        self.dragging = False
        self.pinch_start = None
        self.last_click = 0.0
        self.prev_gesture = Gesture.NONE

    def _map_to_screen(self, x, y):
        x_min, y_min, x_max, y_max = config.ACTIVE_AREA
        # Mantém 1 px de distância das bordas para a mão não disparar o FAILSAFE sem querer
        sx = np.interp(x, (x_min, x_max), (1, self.screen_w - 2))
        sy = np.interp(y, (y_min, y_max), (1, self.screen_h - 2))
        return np.array([sx, sy])

    def _target(self, landmarks):
        return self._map_to_screen(*landmarks[config.CURSOR_LANDMARK])

    def _move(self, landmarks):
        target = self._target(landmarks) + self.drag_offset
        if self.pos is None:
            self.pos = target
        else:
            self.pos = self.pos + (target - self.pos) / config.SMOOTHING
        self.history.append((time.monotonic(), self.pos))
        pyautogui.moveTo(int(self.pos[0]), int(self.pos[1]))

    def _rollback(self, now):
        """Volta o cursor para onde estava antes de os dedos começarem a se fechar."""
        cutoff = now - config.CLICK_ROLLBACK_TIME
        past = [pos for t, pos in self.history if t <= cutoff]
        if past:
            self.pos = past[-1]
        elif self.history:
            self.pos = self.history[0][1]
        else:
            return
        pyautogui.moveTo(int(self.pos[0]), int(self.pos[1]))

    def _click(self, button="left"):
        now = time.monotonic()
        if now - self.last_click >= config.CLICK_COOLDOWN:
            pyautogui.click(button=button)
            self.last_click = now

    def release(self):
        """Solta o botão se estiver arrastando. Chamar ao pausar ou encerrar."""
        if self.dragging:
            pyautogui.mouseUp()
            self.dragging = False
        self.pinch_start = None
        self.drag_offset = np.zeros(2)

    def update(self, gesture, landmarks):
        now = time.monotonic()
        prev, self.prev_gesture = self.prev_gesture, gesture

        if gesture == Gesture.PINCH and landmarks is not None:
            if prev != Gesture.PINCH:
                self.pinch_start = now
                self._rollback(now)
            elif not self.dragging and now - self.pinch_start >= config.DRAG_HOLD_TIME:
                pyautogui.mouseDown()
                self.dragging = True
                if self.pos is not None:
                    self.drag_offset = self.pos - self._target(landmarks)
            # Antes do arrasto começar o cursor fica parado, para o clique cair onde você apontou
            if self.dragging:
                self._move(landmarks)
            return

        # Saiu da pinça: se foi rápida, é clique; se estava arrastando, solta
        if prev == Gesture.PINCH:
            if self.dragging:
                self.release()
            else:
                self._click("left")
            self.pinch_start = None

        if gesture == Gesture.MOVE and landmarks is not None:
            self._move(landmarks)
        elif gesture == Gesture.RIGHT_CLICK and prev != Gesture.RIGHT_CLICK:
            self._click("right")
