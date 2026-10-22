"""Detecção dos 21 pontos da mão com o HandLandmarker do MediaPipe (Tasks API)."""

import time

import cv2
import mediapipe as mp

from handmouse import config

vision = mp.tasks.vision
HAND_CONNECTIONS = vision.HandLandmarksConnections.HAND_CONNECTIONS


class HandTracker:
    def __init__(self, model_path=config.MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em {model_path}. Baixe com:\n"
                "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
                "hand_landmarker/float16/latest/hand_landmarker.task"
            )

        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=config.NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_timestamp = -1

    def process(self, frame_bgr):
        """Retorna os 21 pontos da primeira mão como lista de (x, y) normalizados, ou None."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # O modo VIDEO exige timestamps estritamente crescentes
        timestamp = int(time.monotonic() * 1000)
        if timestamp <= self._last_timestamp:
            timestamp = self._last_timestamp + 1
        self._last_timestamp = timestamp

        result = self.landmarker.detect_for_video(image, timestamp)
        if not result.hand_landmarks:
            return None
        return [(lm.x, lm.y) for lm in result.hand_landmarks[0]]

    @staticmethod
    def draw(frame, landmarks):
        """Desenha os pontos e as conexões da mão no frame."""
        h, w = frame.shape[:2]
        points = [(int(x * w), int(y * h)) for x, y in landmarks]
        for conn in HAND_CONNECTIONS:
            cv2.line(frame, points[conn.start], points[conn.end], (255, 255, 255), 2, cv2.LINE_AA)
        for i, p in enumerate(points):
            color = (0, 200, 255) if i in (4, 8, 12, 16, 20) else (0, 255, 0)
            cv2.circle(frame, p, 4, color, -1, cv2.LINE_AA)

    def close(self):
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
