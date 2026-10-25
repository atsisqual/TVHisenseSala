"""Remove o menu e repõe a função original das teclas. Correr sempre que algo correr mal."""
from _cdp import TV
js = ("clearInterval(window.__tvmenuTimer);"
      "var e=document.getElementById('tvmenu');if(e)e.parentNode.removeChild(e);"
      "if(window.__origDispatch)UI.dispatchKeyEvent=window.__origDispatch;'ok'")
print(TV().ev(js))
