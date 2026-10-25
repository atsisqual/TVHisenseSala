"""Teste reversível de escrita em workRoot 1 (/var/local/applications/UI/).
  python teste_escrita.py --escrever   grava teste_tvmenu.html e lê de volta por file://
  python teste_escrita.py --abrir      abre-a no ecrã da TV (como o E_MANUAL)
  python teste_escrita.py --apagar     apaga o ficheiro de teste
Só mexe num ficheiro: teste_tvmenu.html. Voltar à TV: botão Back/Exit do comando."""
import sys, json
from _cdp import TV
F = "teste_tvmenu.html"
URL = "file:///var/local/applications/UI/" + F
HTML = ("<html><body style='margin:0;background:#101820;color:#fff;font:6vw sans-serif;"
        "display:flex;align-items:center;justify-content:center;height:100vh'>"
        "Pagina guardada na TV: funciona!</body></html>")
tv = TV()
a = sys.argv[1] if len(sys.argv) > 1 else ""
if a == "--escrever":
    print("write ->", tv.ev("Hisense.File.write(%s,%s,1)" % (json.dumps(F), json.dumps(HTML))))
    print("exists ->", tv.ev("Hisense.File.exists(%s,1)" % json.dumps(F)))
    print("lido por file:// ->", tv.ev(
        "(function(){try{var x=new XMLHttpRequest();x.open('GET',%s,false);x.send();return x.responseText.length}catch(e){return 'ERRO '+e}})()" % json.dumps(URL)))
elif a == "--abrir":
    tv.ev("UI.popAllModule(); startThirdPartyApp(APPNAME.E_MANUAL,%s,CMDType.HISENSEPAGE,CMDMethod.COMMANDURL,false); true" % json.dumps(URL))
    print("pedido enviado")
elif a == "--apagar":
    print("delete ->", tv.ev("Hisense.File.delete(%s,1)" % json.dumps(F)))
else:
    print(__doc__)
