"""Captura dos frames da webcam."""

import sys

import cv2

from handmouse import config


class Camera:
    def __init__(self, index=config.CAMERA_INDEX, width=config.FRAME_WIDTH,
                 height=config.FRAME_HEIGHT, mirror=config.MIRROR):
        # No Windows o DirectShow abre a câmera bem mais rápido que o backend padrão
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(index, backend)
        if not self.cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir a câmera {index}.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.mirror = mirror

    def read(self):
        """Retorna o próximo frame em BGR, ou None se a leitura falhar."""
        ok, frame = self.cap.read()
        if not ok:
            return None
        if self.mirror:
            frame = cv2.flip(frame, 1)
        return frame

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.release()
