"""Abre um URL http como app (mesmo caminho das apps instaladas). Uso:
  python abrir_url.py http://192.168.1.127:8099/menu.html [hisense|store]   (por omissão: hisense)
Sair da app: Back/Exit. Usa um nome novo de cada vez para a TV não só repor a app anterior."""
import sys, json, time
from _cdp import TV
url = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.1.127:8099/menu.html"
loja = "StoreType.STORE" if len(sys.argv) > 2 and sys.argv[2] == "store" else "StoreType.HISENSE"
nome = "inicio" + str(int(time.time()))
tv = TV()
print(tv.ev("UI.popAllModule(); startThirdPartyApp(APPNAME.THIRDPARTY,%s,CMDType.NATIVEAPP,CMDMethod.MENU,false,\"#FFFFFF\",%s,%s); 'pedido enviado'" % (json.dumps(url), json.dumps(nome), loja)))
