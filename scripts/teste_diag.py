"""Grava e abre uma página de diagnóstico: mostra no ecrã que objetos existem e que teclas chegam.
Grava teste_diag.html (apagar depois). Sair: Back/Exit."""
import json
from _cdp import TV
F = "teste_diag.html"
URL = "file:///var/local/applications/UI/" + F + "?v=2"
HTML = """<html><head><meta charset=utf-8></head><body style="margin:0;background:#101820;color:#fff;font:2.4vw monospace;padding:3vw">
<div id=o></div><div id=k style="margin-top:2vw;color:#7fdc7f">teclas: (carrega no comando)</div>
<script>
var n=['Hisense','UI','startThirdPartyApp','APPNAME','CMDType','GLOBAL','Config','opera','window.parent','window.opener'];
var s='';
for(var i=0;i<n.length;i++){var t;try{t=typeof eval(n[i])}catch(e){t='ERRO'}s+=n[i]+': '+t+'<br>'}
s+='top==self: '+(window.top===window.self)+'<br>UA: '+navigator.userAgent.slice(0,90);
document.getElementById('o').innerHTML=s;
var log=[];
function reg(e){log.unshift((e.type||'?')+' '+(e.keyCode||e.which)+' '+(e.key||''));log=log.slice(0,6);document.getElementById('k').innerHTML='teclas:<br>'+log.join('<br>')}
document.addEventListener('keydown',reg,true);document.addEventListener('keyup',reg,true);
</script></body></html>"""
tv = TV()
print("write ->", tv.ev("Hisense.File.write(%s,%s,1)" % (json.dumps(F), json.dumps(HTML))))
tv.ev("UI.popAllModule(); startThirdPartyApp(APPNAME.E_MANUAL,%s,CMDType.HISENSEPAGE,CMDMethod.COMMANDURL,false); true" % json.dumps(URL))
print("aberto")
