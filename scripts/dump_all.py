"""Extração em bruto do launcher (SÓ LEITURA). Autónomo: não precisa de _cdp.py.

Faz três coisas e junta tudo em ~/tvdump_raw.tar.gz:
  1. percorre /opt/hisenseUI/ inteiro (ficheiros de texto gravados; o resto fica só na lista _manifest.txt)
  2. lê os ficheiros de dados do launcher (preset, BrowserAppInfo, ...)
  3. grava o estado em memória (mosaicos do ecrã inicial, lista de apps, ...) em _runtime.json

Uso:  python dump_all.py            (só texto)
      python dump_all.py --all      (inclui imagens e outros binários)
"""
import base64, json, os, re, sys, tarfile, urllib.request
import websocket

H = "192.168.1.85:9223"
ROOT = "file:///opt/hisenseUI/"
OUT = os.path.expanduser("~/tvdump_raw")
ALL = "--all" in sys.argv
TEXT = {"js", "json", "html", "htm", "css", "txt", "xml", "ini", "cfg", "conf", "sh", "md", "svg", "csv"}
MAX_FILES, MAX_DEPTH = 6000, 14

page = json.load(urllib.request.urlopen(f"http://{H}/json"))[0]
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=120)
_n = [0]


def ev(expr):
    _n[0] += 1
    ws.send(json.dumps({"id": _n[0], "method": "Runtime.evaluate",
                        "params": {"expression": expr, "returnByValue": True}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == _n[0]:
            return r.get("result", {}).get("result", {}).get("value", None)


# funções auxiliares dentro da página (só leem)
ev(r"""
window.__rd = function(u){
  try{
    var x = new XMLHttpRequest(); x.open('GET', u, false);
    x.overrideMimeType('text/plain; charset=x-user-defined'); x.send();
    var t = x.responseText || '', out = [], CH = 8192;
    for (var i = 0; i < t.length; i += CH) {
      var s = t.substr(i, CH), a = new Array(s.length);
      for (var j = 0; j < s.length; j++) a[j] = String.fromCharCode(s.charCodeAt(j) & 255);
      out.push(a.join(''));
    }
    return btoa(out.join(''));
  } catch(e) { return null; }
};
window.__ls = function(u){
  try { var x = new XMLHttpRequest(); x.open('GET', u, false); x.send(); return x.responseText; }
  catch(e) { return null; }
};
window.__sj = function(o, cap){
  var seen = [];
  try {
    return JSON.stringify(o, function(k, v){
      if (typeof v == 'function') return '[fn]';
      if (v && typeof v == 'object') { if (seen.indexOf(v) > -1) return '[circular]'; seen.push(v); }
      return v;
    }, 1).slice(0, cap || 400000);
  } catch(e) { return 'ERRO ' + e; }
};
true""")

os.makedirs(OUT, exist_ok=True)

# 1. percorrer a pasta da app
ROW = re.compile(r'addRow\("([^"]*)","([^"]*)",(\d),(\d+),')
queue, seen, manifest, saved, skipped = [(ROOT, 0)], set(), [], 0, 0
while queue and len(manifest) < MAX_FILES:
    url, depth = queue.pop(0)
    if url in seen or depth > MAX_DEPTH:
        continue
    seen.add(url)
    html = ev("window.__ls(%s)" % json.dumps(url))
    if not html:
        manifest.append("%s\t(não listável)" % url)
        continue
    for name, esc, isdir, size in ROW.findall(html):
        if name in ("..", "."):
            continue  # nunca subir para fora da pasta da app
        child = url + esc + ("/" if isdir == "1" and not esc.endswith("/") else "")
        if not child.startswith(ROOT):
            continue
        if isdir == "1":
            queue.append((child, depth + 1))
            continue
        rel = child.replace(ROOT, "")
        manifest.append("%s\t%s" % (rel, size))
        ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        if not (ALL or ext in TEXT):
            skipped += 1
            continue
        b64 = ev("window.__rd(%s)" % json.dumps(child))
        if b64 is None:
            manifest.append("%s\t(erro ao ler)" % rel)
            continue
        path = os.path.join(OUT, "app", rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        saved += 1
        if saved % 25 == 0:
            print("  ...", saved, "ficheiros")
open(os.path.join(OUT, "_manifest.txt"), "w").write("\n".join(manifest))
print("app: %d ficheiros gravados, %d só na lista (use --all para os incluir)" % (saved, skipped))

# 2. ficheiros de dados do launcher (leitura)
natives = ["launcher/preset.txt", "launcher/Appinfo.json", "launcher/BrowserAppInfo.json",
           "launcher/deletedPresetApp.txt", "launcher/deletedFoxxumApp.txt",
           "hisenseUI/recentapps.txt", "rAppVersion"]
data = {}
for p in natives:
    data[p] = ev("(function(p){try{return JSON.stringify({exists:Hisense.File.exists(p,1),"
                 "content:Hisense.File.read(p,1)})}catch(e){return 'ERRO '+e}})(%s)" % json.dumps(p))
json.dump(data, open(os.path.join(OUT, "_native_files.json"), "w"), indent=1, ensure_ascii=False)

# 3. estado em memória
state = {}
for name, expr in [
    ("modulo", "UI.getCurrModule().name"),
    ("launcher.currentData", "window.__sj(launcher.currentData)"),
    ("launcher.allAppsData", "window.__sj(launcher.allAppsData)"),
    ("launcher.allInputsData", "window.__sj(launcher.allInputsData)"),
    ("rememberEditApp", "window.__sj(getRememberEditAppFromNativeFile())"),
    ("g_LauncherData", "window.__sj(g_LauncherData)"),
    ("GLOBAL", "window.__sj(GLOBAL, 200000)"),
    ("children", "launcher.children.map(function(c){return (c.name||c.constructor.name)+'/'+c.visible}).join(', ')"),
]:
    state[name] = ev(expr)
json.dump(state, open(os.path.join(OUT, "_runtime.json"), "w"), indent=1, ensure_ascii=False)

# juntar tudo
tar = os.path.expanduser("~/tvdump_raw.tar.gz")
with tarfile.open(tar, "w:gz") as t:
    t.add(OUT, arcname="tvdump_raw")
print("Pronto:", tar, "(%.1f MB)" % (os.path.getsize(tar) / 1e6))
