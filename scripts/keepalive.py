"""Mantém o menu ligado: se a TV reiniciar (ou a interface recarregar), volta a injetar o menu.
Correr num dispositivo sempre ligado na mesma rede (telemóvel, PC, Raspberry Pi). Ctrl+C para parar.
Usar só depois de confirmar com menu.py que as teclas e o OK funcionam. Desligar o menu: off.py"""
import json, time, urllib.request
import websocket
from menu_js import JS

H = "192.168.1.85:9223"
INTERVALO = 10


def verificar():
    page = json.load(urllib.request.urlopen(f"http://{H}/json", timeout=5))[0]
    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=15)

    def ev(expr):
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression": expr, "returnByValue": True}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == 1:
                return r.get("result", {}).get("result", {}).get("value")

    try:
        if ev("typeof window.__tvmenuTimer") == "undefined":
            ev(JS)
            return True
        return False
    finally:
        ws.close()


falhou = False
while True:
    try:
        if verificar():
            print(time.strftime("%H:%M:%S"), "menu (re)injetado")
        falhou = False
    except Exception as e:
        if not falhou:
            print(time.strftime("%H:%M:%S"), "TV inacessível, a tentar de novo:", type(e).__name__)
        falhou = True
    time.sleep(INTERVALO)
