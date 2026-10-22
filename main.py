"""HandMouse: loop principal.

Teclas:
  F8  (global) ou P (na janela)  pausa / retoma o controle
  F10 (global) ou Q / Esc (na janela)  encerra
"""

import time

import cv2
import pyautogui

from handmouse import config
from handmouse.camera import Camera
from handmouse.gesture_detector import Gesture, GestureDetector
from handmouse.hand_tracker import HandTracker
from handmouse.hotkeys import HotkeyWatcher
from handmouse.mouse_controller import MouseController


def draw_overlay(frame, gesture, paused, fps, detector):
    h, w = frame.shape[:2]
    x_min, y_min, x_max, y_max = config.ACTIVE_AREA
    cv2.rectangle(frame, (int(x_min * w), int(y_min * h)), (int(x_max * w), int(y_max * h)),
                  (255, 0, 255), 2)

    cv2.putText(frame, f"Gesto: {gesture.value}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 1, cv2.LINE_AA)
    if paused:
        cv2.putText(frame, "PAUSADO (palma 1s ou F8 retoma)", (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2, cv2.LINE_AA)
    if config.DEBUG and detector.last_ratio is not None:
        fingers = "".join("1" if f else "0" for f in detector.last_fingers)
        cv2.putText(frame, f"Pinca: {detector.last_ratio:.2f} (< {config.PINCH_ON_THRESHOLD})"
                    f"  Dedos: {fingers}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 2, cv2.LINE_AA)
    if not config.MOUSE_ENABLED:
        cv2.putText(frame, "Mouse desativado (config.MOUSE_ENABLED)", (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1, cv2.LINE_AA)


def run():
    detector = GestureDetector()
    mouse = MouseController() if config.MOUSE_ENABLED else None
    hotkeys = HotkeyWatcher()
    paused = False
    palm_start = None  # quando a palma aberta começou; None depois de já ter alternado
    fps, last_time = 0.0, time.monotonic()
    last_debug = 0.0

    with Camera() as camera, HandTracker() as tracker:
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    print("Falha ao ler a câmera.")
                    break

                landmarks = tracker.process(frame)
                gesture = detector.update(landmarks)

                # Teclas: atalhos globais e teclas da janela
                key = cv2.waitKey(1) & 0xFF if config.SHOW_WINDOW else 255
                if hotkeys.pressed(config.HOTKEY_EXIT) or key in (ord("q"), 27):
                    break
                toggle = hotkeys.pressed(config.HOTKEY_TOGGLE_PAUSE) or key == ord("p")

                # Palma aberta mantida alterna a pausa, uma vez por gesto
                now = time.monotonic()
                if gesture != Gesture.PAUSE:
                    palm_start = now
                elif palm_start is not None and now - palm_start >= config.PAUSE_HOLD_TIME:
                    toggle = True
                    palm_start = None

                if toggle:
                    paused = not paused
                    if paused and mouse:
                        mouse.release()
                        mouse.prev_gesture = Gesture.NONE  # não clicar ao retomar no meio de uma pinça

                if mouse and not paused:
                    mouse.update(gesture, landmarks)

                if config.DEBUG and detector.last_ratio is not None and now - last_debug >= 0.25:
                    fingers = "".join("1" if f else "0" for f in detector.last_fingers)
                    print(f"pinca={detector.last_ratio:.2f} dedos={fingers} gesto={gesture.name}"
                          f"{' PAUSADO' if paused else ''}", flush=True)
                    last_debug = now

                fps = 0.9 * fps + 0.1 / max(now - last_time, 1e-6)
                last_time = now

                if config.SHOW_WINDOW:
                    if landmarks:
                        tracker.draw(frame, landmarks)
                    draw_overlay(frame, gesture, paused, fps, detector)
                    cv2.imshow(config.WINDOW_NAME, frame)
        except pyautogui.FailSafeException:
            print("FAILSAFE acionado (mouse no canto da tela). Encerrando.")
        except KeyboardInterrupt:
            pass
        finally:
            if mouse:
                pyautogui.FAILSAFE = False  # permite soltar o botão mesmo com o mouse no canto
                mouse.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
