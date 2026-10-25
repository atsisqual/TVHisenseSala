"""Descarrega para ./tvdump todos os scripts que o launcher carrega (só leitura)."""
import os
from _cdp import TV
tv = TV()
os.makedirs("tvdump", exist_ok=True)
scripts = tv.ev("Array.from(document.scripts).map(function(s){return s.src}).filter(Boolean)")
base = "file:///opt/hisenseUI/html/hisenseUI/"
ok = 0
for src in scripts:
    rel = src.replace(base, "")
    code = tv.ev("(function(){try{var x=new XMLHttpRequest();x.open('GET','%s',false);x.send();return x.responseText}catch(e){return null}})()" % src)
    if code:
        path = os.path.join("tvdump", rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write(code)
        ok += 1
print("scripts gravados:", ok, "de", len(scripts))
