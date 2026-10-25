"""SÓ LEITURA. Mostra o que há em /var/local/applications/UI/launcher/ e /hisenseUI/ (workRoot 1)
e se rememberEditApp.json está lá."""
import json, re
from _cdp import TV
ROW = re.compile(r'addRow\("([^"]*)","([^"]*)",(\d),(\d+),')
tv = TV()
tv.ev("""window.__ls=function(u){try{var x=new XMLHttpRequest();x.open('GET',u,false);x.send();return x.responseText}catch(e){return null}};true""")
for p in ["launcher/", "hisenseUI/"]:
    html = tv.ev("window.__ls(%s)" % json.dumps("file:///var/local/applications/UI/" + p))
    print("==", p)
    if not html:
        print("  (não listável)")
        continue
    for n, esc, d, s in ROW.findall(html):
        if n not in ("..", "."):
            print("  %s %s %s" % ("[d]" if d == "1" else "   ", n, "" if d == "1" else s + " B"))
print("== exists rememberEditApp.json (workRoot 1):",
      tv.ev("Hisense.File.exists('launcher/rememberEditApp.json',1)"))
