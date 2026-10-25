"""Grava e abre (file://) uma página que regista TODOS os eventos que recebe (teclas, rato, roda, foco).
Serve para perceber como o comando chega a páginas locais. Sair: Back/Exit. Apagar: Hisense.File.delete('teste_eventos.html',1)."""
import json, time
from _cdp import TV
F = "teste_eventos.html"
URL = "file:///var/local/applications/UI/" + F + "?v=" + str(int(time.time()))
HTML = r"""<html><head><meta charset=utf-8></head><body style="margin:0;background:#101820;color:#fff;font:2vw monospace;padding:2vw">
<div>Eventos recebidos (carrega nas setas, OK, mexe o cursor):</div>
<div id=n style="margin-top:1vw;color:#ffd24a"></div>
<div id=l style="margin-top:1vw;color:#7fdc7f;white-space:pre"></div>
<div id=b style="position:absolute;left:55vw;top:30vh;width:30vw;height:30vh;background:#2a6;border-radius:2vw;text-align:center;line-height:30vh" onmouseover="this.style.background='#e63'" onmouseout="this.style.background='#2a6'" onclick="this.innerHTML='CLIQUE!'">caixa de teste (passa o cursor / OK)</div>
<script>
var c={},log=[];
function reg(e){var t=e.type;c[t]=(c[t]||0)+1;
 var x=t+' '+(e.keyCode||e.which||'')+(e.clientX!==undefined?' x'+e.clientX+' y'+e.clientY:'')+(e.target&&e.target.id?' @'+e.target.id:'');
 log.unshift(x);log=log.slice(0,9);
 var s='';for(var k in c)s+=k+':'+c[k]+'  ';
 document.getElementById('n').innerHTML=s;document.getElementById('l').innerHTML=log.join('\n')}
['keydown','keyup','keypress','mousemove','mousedown','mouseup','click','wheel','mousewheel','focus','blur','touchstart','contextmenu','mouseover'].forEach(function(t){document.addEventListener(t,reg,true);window.addEventListener(t,reg,true)});
document.getElementById('n').innerHTML='(nada ainda)';
</script></body></html>"""
tv = TV()
print("write ->", tv.ev("Hisense.File.write(%s,%s,1)" % (json.dumps(F), json.dumps(HTML))))
nome = "ev" + str(int(time.time()))
tv.ev("UI.popAllModule(); startThirdPartyApp(APPNAME.THIRDPARTY,%s,CMDType.NATIVEAPP,CMDMethod.MENU,false,\"#FFFFFF\",%s,StoreType.HISENSE); true" % (json.dumps(URL), json.dumps(nome)))
print("aberto")
