"""Procura em que pasta da TV está o ficheiro rAppVersion (o que o launcher grava com workRoot 1).
SÓ LEITURA: lista nomes de pastas (não lê conteúdos). Deteção pelo NOME na listagem, não pelo tamanho."""
import json, re, urllib.request
import websocket

H = "192.168.1.85:9223"
ALVO = "rAppVersion"
RAIZES = ["/var/local/", "/applications/", "/appcache/", "/database/", "/config/", "/hidata/",
          "/Customer/", "/CustomerBackup/", "/tvdatabase/", "/tvconfig/", "/tvcustomer/",
          "/tvservice/", "/serialdata/", "/system/", "/vddt/", "/vendor/", "/subsystem/"]
SALTAR = ("image-cache", "lost+found", "netflix", "logservice", "IQQIRuntimeDB", "wifi", "bluedroid", "avs")
MAX_PROF, MAX_PASTAS = 3, 400
ROW = re.compile(r'addRow\("([^"]*)","([^"]*)",(\d),(\d+),')


def listar(ev, caminho):
    html = ev("window.__ls(%s)" % json.dumps("file://" + caminho))
    if not html:
        return None
    return [(n, esc, t == "1") for n, esc, t, _ in ROW.findall(html) if n not in ("..", ".")]


def procurar(ev):
    achados, vistas, fila = [], 0, [(r, 0) for r in RAIZES]
    while fila and vistas < MAX_PASTAS:
        pasta, prof = fila.pop(0)
        itens = listar(ev, pasta)
        vistas += 1
        if itens is None:
            continue
        for nome, esc, e_dir in itens:
            if not e_dir and nome == ALVO:
                achados.append(pasta)
            if e_dir and prof < MAX_PROF and nome not in SALTAR:
                fila.append((pasta + esc + "/", prof + 1))
    return achados, vistas


if __name__ == "__main__":
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

    ev(r"""window.__ls = function(u){ try { var x = new XMLHttpRequest(); x.open('GET', u, false); x.send();
        return x.responseText; } catch(e) { return null; } }; true""")
    achados, vistas = procurar(ev)
    print("pastas listadas:", vistas)
    if achados:
        for a in achados:
            print("ENCONTRADO", ALVO, "em:", a)
            itens = listar(ev, a)
            print("   conteúdo:", ", ".join(("[d] " if d else "") + n for n, _, d in itens)[:400])
    else:
        print("não encontrado nestas pastas")
    for extra in ["/var/local/applications/", "/var/local/appdata/"]:
        itens = listar(ev, extra)
        print(extra, "->", "não listável" if itens is None else ", ".join(("[d] " if d else "") + n for n, _, d in itens)[:400])
