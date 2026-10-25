"""Menu estilo Android TV, só no ecrã Smart (launcher.children[3] == allApps).
Teclas: 37 esquerda, 39 direita, 13 OK. Cima/baixo escondem o menu. As restantes passam sempre.
Em memória apenas. Desligar: off.py"""
from _cdp import TV
from menu_js import JS

print(TV().ev(JS))
