"""Mostra as últimas teclas recebidas pelo menu (diagnóstico)."""
from _cdp import TV
print(TV().ev("JSON.stringify(window.__dk)"))
