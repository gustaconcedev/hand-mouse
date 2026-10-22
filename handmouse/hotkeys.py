"""Teclas de atalho globais, para recuperar o controle mesmo com a janela sem foco.

Usa a API do Windows via ctypes, sem dependências extras. Em outros sistemas não faz nada.
"""

import sys

if sys.platform == "win32":
    import ctypes

    _get_key_state = ctypes.windll.user32.GetAsyncKeyState
else:
    _get_key_state = None


class HotkeyWatcher:
    def __init__(self):
        self._down = set()

    def pressed(self, vk_code):
        """True apenas no frame em que a tecla passa de solta para pressionada."""
        if _get_key_state is None:
            return False
        is_down = bool(_get_key_state(vk_code) & 0x8000)
        was_down = vk_code in self._down
        if is_down:
            self._down.add(vk_code)
        else:
            self._down.discard(vk_code)
        return is_down and not was_down
