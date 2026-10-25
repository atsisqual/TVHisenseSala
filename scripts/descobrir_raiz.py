"""Descobre onde a TV guarda os dados do launcher (workRoot 1). SÓ LEITURA.
Procura ficheiros que a própria TV já escreveu em vários diretórios e lista nomes de pastas."""
import json, re, urllib.request
import websocket

H = "192.168.1.85:9223"
page = json.load(urllib.request.urlopen(f"http://{H}/json"))[0]
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)
_n = [0]


def ev(expr):
    _n[0] += 1
    ws.send(json.dumps({"id": _n[0], "method": "Runtime.evaluate",
                        "params": {"expression": expr, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == _n[0]:
            return r.get("result", {}).get("result", {}).get("value", None)


ev(r"""
window.__ex = function(u){
  try { var x = new XMLHttpRequest(); x.open('GET', u, false); x.send();
        var t = x.responseText; return (t === null || t === undefined) ? null : t.length; }
  catch(e) { return null; }
};
window.__ls = function(u){
  try { var x = new XMLHttpRequest(); x.open('GET', u, false); x.send(); return x.responseText; }
  catch(e) { return null; }
};
true""")

ficheiros = ["rAppVersion", "launcher/rememberEditApp.json"]
bases = ["/var/local/hisenseUI/", "/var/local/", "/3rd_rw/", "/3rd_rw/hisenseUI/", "/3rd_rw/UI/",
         "/var/local/launcher/", "/opt/hisenseUI/appdata/", "/tmp/", "/dev/shm/", "/data/", "/mnt/"]
print("== procurar os ficheiros que a TV já escreveu (workRoot 1) ==")
achou = False
for b in bases:
    for f in ficheiros:
        n = ev("window.__ex(%s)" % json.dumps("file://" + b + f))
        if n is not None:
            print("  ENCONTRADO: file://%s%s  (%d bytes)" % (b, f, n))
            achou = True
if not achou:
    print("  não encontrado nestas pastas")

ROW = re.compile(r'addRow\("([^"]*)","([^"]*)",(\d),(\d+),')
print("\n== nomes nas pastas de dados (só nomes) ==")
for d in ["/", "/var/local/", "/3rd_rw/", "/var/local/hisenseUI/", "/3rd_rw/UI/"]:
    html = ev("window.__ls(%s)" % json.dumps("file://" + d))
    if not html:
        print(" ", d, "-> não listável")
        continue
    nomes = [("[d] " if t == "1" else "") + n for n, _, t, _ in ROW.findall(html) if n not in ("..", ".")]
    print(" ", d, "->", ", ".join(nomes[:40]) + (" ..." if len(nomes) > 40 else ""))
