"""Troca o endereço de uma app instalada em launcher/Appinfo.json e launcher/preset.txt (com cópia .bak).
  python trocar_url.py ANTIGO NOVO     troca (substituição de texto; o JSON continua válido)
  python trocar_url.py --desfazer      repõe as cópias .bak e apaga-as
Depois: python reload.py (recarrega o launcher para ele reler os ficheiros)."""
import sys, json
from _cdp import TV
FILES = ["launcher/Appinfo.json", "launcher/preset.txt"]
tv = TV()
def rd(p): return tv.ev("(function(){try{return Hisense.File.read(%s,1)}catch(e){return null}})()" % json.dumps(p))
def wr(p, c): return tv.ev("Hisense.File.write(%s,%s,1)" % (json.dumps(p), json.dumps(c)))
if sys.argv[1:2] == ["--desfazer"]:
    for f in FILES:
        b = rd(f + ".bak")
        if b: print(f, "reposto ->", wr(f, b), "| apagar .bak ->", tv.ev("Hisense.File.delete(%s,1)" % json.dumps(f + ".bak")))
        else: print(f, "sem .bak (nada a repor)")
elif len(sys.argv) == 3:
    old, new = sys.argv[1], sys.argv[2]
    for f in FILES:
        c = rd(f)
        if not c or old not in c: print(f, "não contém", old); continue
        if not rd(f + ".bak"): print(f, "cópia .bak ->", wr(f + ".bak", c))
        r = c.replace(old, new); json.loads(r)  # valida JSON antes de gravar
        print(f, "trocados", c.count(old), "->", wr(f, r))
else:
    print(__doc__)
