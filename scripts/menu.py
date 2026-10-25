"""Menu estilo Android TV, só no ecrã Smart (launcher.children[3] == allApps).
Teclas: 37 esquerda, 39 direita, 13 OK. Cima/baixo escondem o menu. As restantes passam sempre.
Em memória apenas. Desligar: off.py"""
from _cdp import TV
JS = r"""
(function(){
 if (window.__tvmenuTimer) clearInterval(window.__tvmenuTimer);
 var old = document.getElementById('tvmenu'); if (old) old.parentNode.removeChild(old);
 if (!window.__origDispatch) window.__origDispatch = UI.dispatchKeyEvent;
 UI.dispatchKeyEvent = window.__origDispatch;
 var TILES = [
  ['Netflix','NETFLIX','#b20710','netflix.png'],
  ['YouTube','YOUTUBE','#c4302b','youtube.png'],
  ['Dailymotion','DAILYMOTION','#0b57d0','Dailymotion.png'],
  ['Meteo','ACCUWEATHER','#1f7a4d','accuweather.png'],
  ['Jogos','GAMECENTER','#6b46c1','gamecenter.png'],
  ['Browser','TVBROWSER','#2b6cb0','TVBrowser.png']
 ];
 var idx = 0, shown = false, dismissed = false;
 var el = document.createElement('div'); el.id = 'tvmenu';
 el.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;z-index:99999;display:none;background:linear-gradient(#0b0f19,#1c2540);color:#fff;font-family:Arial,sans-serif;overflow:hidden';
 var clock = document.createElement('div');
 clock.style.cssText = 'position:absolute;right:5vw;top:5vh;font-size:4.5vw';
 var title = document.createElement('div');
 title.style.cssText = 'position:absolute;left:5vw;top:7vh;font-size:3vw;color:#9aa4b8';
 title.innerHTML = 'Aplicações';
 var row = document.createElement('div');
 row.style.cssText = 'position:absolute;left:5vw;top:40vh;white-space:nowrap';
 el.appendChild(clock); el.appendChild(title); el.appendChild(row);
 var tiles = [];
 for (var i = 0; i < TILES.length; i++) {
  var t = document.createElement('div');
  t.style.cssText = 'display:inline-block;width:14vw;height:9vw;margin-right:1.2vw;border-radius:1vw;vertical-align:top;position:relative;background:' + TILES[i][2];
  var img = document.createElement('img');
  img.src = 'launcher/app/launcher1/' + TILES[i][3];
  img.style.cssText = 'position:absolute;left:50%;top:8%;max-width:60%;max-height:50%;-webkit-transform:translateX(-50%);transform:translateX(-50%)';
  img.onerror = function(){ this.style.display = 'none'; };
  var lab = document.createElement('div');
  lab.style.cssText = 'position:absolute;left:0;right:0;bottom:7%;text-align:center;font-size:1.7vw';
  lab.innerHTML = TILES[i][0];
  t.appendChild(img); t.appendChild(lab);
  row.appendChild(t); tiles.push(t);
 }
 document.body.appendChild(el);
 function sel(n){
  if (n < 0 || n >= tiles.length) return;
  tiles[idx].style.boxShadow = 'none'; tiles[idx].style.webkitTransform = 'none'; tiles[idx].style.transform = 'none';
  idx = n;
  tiles[idx].style.boxShadow = '0 0 0 0.35vw #fff, 0 1vw 3vw rgba(0,0,0,.7)';
  tiles[idx].style.webkitTransform = 'scale(1.12)'; tiles[idx].style.transform = 'scale(1.12)';
 }
 function pad(x){ return (x < 10 ? '0' : '') + x; }
 function onApps(){
  try {
   if (UI.getCurrModule().name != 'launcher') return false;
   var c = launcher.children[3];
   return !!c && ((c.name || c.constructor.name) == 'allApps');
  } catch(e) { return false; }
 }
 function show(v){ shown = v; el.style.display = v ? 'block' : 'none'; if (v) sel(idx); }
 function tick(){
  var d = new Date(); clock.innerHTML = pad(d.getHours()) + ':' + pad(d.getMinutes());
  var apps = onApps();
  if (!apps) { dismissed = false; if (shown) show(false); return; }
  if (!dismissed && !shown) show(true);
 }
 function launch(){
  var k = TILES[idx][1];
  show(false); dismissed = true;
  UI.popAllModule();
  startThirdPartyApp(APPNAME[k], APPNAME[k], CMDType.NATIVEAPP, CMDMethod.MENU, false);
 }
 window.__dk = [];
 UI.dispatchKeyEvent = function(k){
  var c = k;
  try { if (k && typeof k == 'object') c = (k.keyCode !== undefined ? k.keyCode : (k.which !== undefined ? k.which : (k.key !== undefined ? k.key : k.code))); } catch(e){}
  try { window.__dk.push((typeof k) + ':' + String(c)); if (window.__dk.length > 30) window.__dk.shift(); } catch(e){}
  if (shown) {
   if (c == 37) { sel(idx - 1); return; }
   if (c == 39) { sel(idx + 1); return; }
   if (c == 13) { launch(); return; }
   if (c == 38 || c == 40) { show(false); dismissed = true; }
  }
  return window.__origDispatch.apply(this, arguments);
 };
 window.__tvmenuTimer = setInterval(tick, 700);
 tick();
 return 'menu ligado; ecra de apps = ' + onApps();
})()
"""
print(TV().ev(JS))
