# Diário de Bordo — HandMouse

Controle do mouse e do teclado por gestos da mão, usando a webcam.

## 1. Visão geral

1. **Captura da webcam**: o Python recebe os frames da câmera continuamente.
2. **Detecção da mão**: o MediaPipe identifica os 21 pontos de referência da mão (articulações e pontas dos dedos).
3. **Interpretação dos gestos**: o programa calcula posições e distâncias entre os pontos para descobrir se a mão está apontando, fazendo pinça ou fechada.
4. **Execução da ação**: o programa move o cursor, clica ou executa comandos no sistema operacional.

```
Webcam → OpenCV → MediaPipe → Interpretador de gestos → PyAutoGUI → Mouse/teclado
```

## 2. Bibliotecas

| Biblioteca | Função |
|---|---|
| opencv-python | Captura e processamento dos frames; janela com a mão e os pontos |
| mediapipe | Detecção da mão e dos 21 pontos (Tasks API, `HandLandmarker`) |
| pyautogui | Controle do mouse e do teclado |
| numpy | Distâncias, normalização e mapeamento de coordenadas |

## 3. Gestos

| Gesto | Ação |
|---|---|
| Indicador levantado | Move o cursor seguindo a ponta do indicador |
| Pinça (indicador + polegar) | Clique esquerdo |
| Pinça mantida | Segura o botão esquerdo (arrastar) |
| Palma aberta | Pausa o controle (modo de segurança) |
| Indicador + médio levantados | Clique direito |

Os gestos são regras matemáticas sobre os pontos do MediaPipe; não há treinamento de modelo.

## 4. Arquitetura

```
hand-mouse/
├── main.py              # loop principal, tecla de saída, modo pausa
├── config.py            # resolução, área útil, suavização, limiares, cooldown
├── camera.py            # captura da webcam
├── hand_tracker.py      # HandLandmarker (modo VIDEO), retorna 21 pontos
├── gesture_detector.py  # dedos levantados, pinça, estabilização por frames
├── mouse_controller.py  # mapeamento câmera→tela, suavização, cliques e arrasto
├── models/
│   └── hand_landmarker.task
├── requirements.txt
└── README.md
```

Fluxo por frame: `camera` → `hand_tracker` → `gesture_detector` → `mouse_controller` → desenho na tela, com `main` mantendo o ciclo.

## 5. Desafios técnicos

| Desafio | Solução |
|---|---|
| Cursor tremendo | Filtro exponencial: `pos = pos_ant + (alvo - pos_ant) / fator` |
| Mapeamento de coordenadas | Área útil menor na câmera convertida para a tela com `np.interp` |
| Cliques acidentais | Gesto estável por K frames e intervalo mínimo entre cliques |
| Pinça independente da distância | Distância entre os pontos 4 e 8 dividida pelo tamanho da mão (pontos 0 a 9) |
| Desempenho | Câmera em 640x480, `pyautogui.PAUSE = 0`, MediaPipe em modo VIDEO |
| Segurança | Tecla para pausar ou sair, palma aberta pausa, `FAILSAFE` do PyAutoGUI ativo |

## 6. Plano de desenvolvimento

1. **Etapa 1 — Reconhecer a mão**: abrir a webcam e desenhar os pontos e conexões, sem controlar o mouse.
2. **Etapa 2 — Mover o cursor**: ponta do indicador controla o cursor; calibrar sensibilidade e suavização.
3. **Etapa 3 — Cliques**: pinça para clique esquerdo, clique direito e arrasto, com proteção contra comandos duplicados.
4. **Etapa 4 — Interface de configuração**: ajustar sensibilidade, gestos, área de rastreamento, ativação e pausa.
5. **Etapa 5 — Aplicação distribuível**: dependências, tratamento de erros, documentação e executável.

## 7. Ambiente

- Python 3.15, executado pelo launcher `py` (o comando `python` não está no PATH).
- Versões instaladas: opencv-python 5.0.0.93, mediapipe 1.1.1, PyAutoGUI 0.9.54, numpy 2.5.4.
- O `opencv-contrib-python` também está instalado e pode conflitar com o `opencv-python`.
- Repositório: https://github.com/gustaconcedev/hand-mouse.git
- Branch base: `handmouse-master`.

## 8. Registro de alterações

| Data | Branch | Alteração |
|---|---|---|
| 2026-10-22 | handmouse-master | Repositório criado; diário de bordo com a ideia do projeto |
| 2026-10-22 | handmouse#01 | Diário de bordo movido para `docs/diario de bordo/` |
