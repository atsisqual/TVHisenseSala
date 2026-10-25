"""Recarrega a interface da TV (apaga tudo o que foi injetado). Ecrã preto 20-40 s."""
import json
from _cdp import connect
ws = connect()
ws.send(json.dumps({"id": 1, "method": "Page.reload", "params": {"ignoreCache": True}}))
print(ws.recv())
