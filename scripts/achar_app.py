"""SÓ LEITURA. Procura em /var/local onde a TV guardou as apps instaladas (ficheiros que contêm '192.168.1.127' ou '8099')."""
import json, re
from _cdp import TV
ROW = re.compile(r'addRow\("([^"]*)","([^"]*)",(\d),(\d+),')
SALTAR = ("image-cache", "lost+found", "netflix", "logservice", "IQQIRuntimeDB", "wifi", "bluedroid", "avs", "Fontconfig", "cache")
ALVOS = ("192.168.1.127", "8099")
tv = TV()
tv.ev("""window.__ls=function(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.send();return x.responseText}catch(e){return null}};
window.__rd=function(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.overrideMimeType('text/plain; charset=utf-8');x.send();return x.responseText}catch(e){return null}};true""")
fila, vistos, achados, n = [("file:///var/local/", 0)], 0, [], 0
while fila and vistos < 600:
    url, prof = fila.pop(0)
    html = tv.ev("window.__ls(%s)" % json.dumps(url)); vistos += 1
    if not html: continue
    for nome, esc, d, tam in ROW.findall(html):
        if nome in ("..", "."): continue
        f = url + esc + ("/" if d == "1" and not esc.endswith("/") else "")
        if d == "1":
            if prof < 5 and nome not in SALTAR: fila.append((f, prof + 1))
        elif int(tam) < 300000:
            n += 1
            txt = tv.ev("window.__rd(%s)" % json.dumps(f)) or ""
            if any(a in txt for a in ALVOS):
                achados.append(f); i = min([txt.find(a) for a in ALVOS if a in txt])
                print("ENCONTRADO", f.replace("file://", ""), "(%s B)" % tam); print("   ...", txt[max(0, i-200):i+200].replace("\n", " "))
print("pastas vistas:", vistos, "| ficheiros lidos:", n, "| encontrados:", len(achados))
