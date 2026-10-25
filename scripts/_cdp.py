import json, urllib.request, websocket
H = "192.168.1.85:9223"

def connect():
    page = json.load(urllib.request.urlopen(f"http://{H}/json"))[0]
    return websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)

class TV:
    def __init__(self):
        self.ws = connect()
        self.n = 0
    def ev(self, expr):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": "Runtime.evaluate",
            "params": {"expression": expr, "returnByValue": True}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.n:
                return r.get("result", {}).get("result", {}).get("value", r)
