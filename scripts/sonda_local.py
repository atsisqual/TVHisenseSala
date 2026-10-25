"""SÓ LEITURA. Sonda portas HTTP em 127.0.0.1 a partir da própria TV (via launcher).
  python sonda_local.py          testa as portas conhecidas e comuns
  python sonda_local.py --tudo   varre 1-65535 (pode demorar vários minutos)"""
import sys, json, time
from _cdp import TV
tv = TV()
tv.ev("""window.__p=function(port){try{var x=new XMLHttpRequest();x.open('GET','http://127.0.0.1:'+port+'/',false);x.send();
 return {s:x.status,t:(x.getResponseHeader('Content-Type')||'')+' | '+(x.getResponseHeader('Server')||''),b:(x.responseText||'').slice(0,100).replace(/\\s+/g,' ')}}catch(e){return null}};true""")
# sanidade: a 9223 sabemos que responde
r = tv.ev("window.__p(9223)")
print("sanidade 127.0.0.1:9223 ->", r)
if not r:
    print("A TV não deixa o launcher ligar a 127.0.0.1 por XHR: a sonda não é fiável.")
CONHECIDAS = [80, 81, 443, 1969, 2121, 2122, 2123, 3822, 3823, 3824, 3825, 3826, 5978, 8000, 8008, 8080, 8081, 8443, 8888, 9000,
              9223, 10001, 12321, 36669, 38400, 39500, 47241, 54486, 56789, 56790, 7000, 7001, 4000, 3000, 5000, 6000, 1234, 9090]
portas = range(1, 65536) if "--tudo" in sys.argv else CONHECIDAS
t0 = time.time(); achados = []
for p in portas:
    r = tv.ev("window.__p(%d)" % p)
    if r:
        achados.append(p); print("RESPONDE", p, r)
    if time.time() - t0 > 900: print("(limite de tempo)"); break
print("fim. portas que responderam:", achados)
