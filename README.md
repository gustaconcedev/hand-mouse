# HandMouse

Controle do mouse por gestos da mão, usando a webcam.

```
Webcam → OpenCV → MediaPipe → Interpretador de gestos → PyAutoGUI → Mouse
```

## Instalação

```
py -m pip install -r requirements.txt
```

O modelo `models/hand_landmarker.task` já vem no repositório. Se precisar baixá-lo de novo:
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

## Uso

```
py main.py
```

| Gesto | Ação |
|---|---|
| Indicador levantado | Move o cursor |
| Pinça rápida (polegar + indicador) | Clique esquerdo |
| Pinça mantida | Arrastar |
| Indicador + médio levantados | Clique direito |
| Palma aberta | Pausa o controle |

| Tecla | Ação |
|---|---|
| F8 (em qualquer janela) ou P (na janela do HandMouse) | Pausa / retoma |
| F10 (em qualquer janela) ou Q / Esc (na janela do HandMouse) | Encerra |
| Levar o mouse físico a um canto da tela | Encerra (FAILSAFE do PyAutoGUI) |

Mova a mão dentro do retângulo roxo da janela: ele corresponde à tela inteira.

## Estrutura

```
hand-mouse/
├── main.py                  # loop principal, teclas, pausa
├── handmouse/
│   ├── config.py            # câmera, área útil, suavização, limiares, atalhos
│   ├── camera.py            # captura da webcam
│   ├── hand_tracker.py      # HandLandmarker (modo VIDEO), 21 pontos da mão
│   ├── gesture_detector.py  # dedos levantados, pinça, estabilização por frames
│   ├── mouse_controller.py  # mapeamento câmera→tela, suavização, cliques, arrasto
│   └── hotkeys.py           # atalhos globais (Windows)
├── models/
│   └── hand_landmarker.task
└── docs/diario de bordo/    # diário de bordo do projeto
```

## Calibração

Tudo fica em `handmouse/config.py`. Para testar só o reconhecimento da mão, sem mexer no mouse, use `MOUSE_ENABLED = False`.
