"""SÓ LEITURA. Sonda portas HTTP em 127.0.0.1 a partir da própria TV (pedidos assíncronos, limite 3 s).
  python sonda_local.py          portas conhecidas e comuns
  python sonda_local.py --tudo   1-65535 (alguns minutos)"""
import sys, json, time
from _cdp import TV
tv = TV()
tv.ev("""window.__R={};window.__n=0;window.__tot=0;
window.__probe=function(p){var x=new XMLHttpRequest();window.__tot++;var fim=function(r){if(window.__R[p]===undefined){window.__R[p]=r;window.__n++}};
 try{x.open('GET','http://127.0.0.1:'+p+'/',true);x.timeout=3000;
 x.onload=function(){fim({s:x.status,t:(x.getResponseHeader('Content-Type')||'')+' | '+(x.getResponseHeader('Server')||''),b:(x.responseText||'').slice(0,100).replace(/\\s+/g,' ')})};
 x.onerror=function(){fim(null)};x.ontimeout=function(){fim('timeout')};x.send()}catch(e){fim(null)}};
window.__go=function(ports,lote){var i=0;(function next(){var f=0;while(i<ports.length&&f<lote){window.__probe(ports[i++]);f++}
 if(i<ports.length)setTimeout(function(){if(window.__tot-window.__n>lote)setTimeout(next,300);else next()},40);else window.__fim=true})()};
true""")
CONHECIDAS = [80, 81, 443, 1969, 2121, 2122, 2123, 3822, 3823, 3824, 3825, 3826, 5978, 8000, 8008, 8080, 8081, 8443, 8888, 9000,
              9223, 10001, 12321, 36669, 38400, 39500, 47241, 54486, 56789, 56790, 7000, 7001, 4000, 3000, 5000, 6000, 1234, 9090]
portas = list(range(1, 65536)) if "--tudo" in sys.argv else CONHECIDAS
tv.ev("window.__fim=false;window.__go(%s,%d);true" % (json.dumps(portas), 25))
t0 = time.time(); ult = -1
while time.time() - t0 < 1800:
    time.sleep(3)
    n, fim = tv.ev("[window.__n, !!window.__fim]")
    if n != ult and n % 500 == 0 or fim: print("  ...", n, "de", len(portas))
    ult = n
    if fim and n >= len(portas) - 25: break
time.sleep(4)
R = json.loads(tv.ev("JSON.stringify(window.__R)"))
for p in sorted(R, key=int):
    if isinstance(R[p], dict): print("RESPONDE HTTP", p, R[p])
tm = [p for p in sorted(R, key=int) if R[p] == "timeout"]
print("ligam mas não respondem (timeout):", tm)
