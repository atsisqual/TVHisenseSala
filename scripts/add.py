"""Acrescenta um mosaico (lista de Apps) através de launcher/BrowserAppInfo.json."""
import json, time
from _cdp import TV
TITLE = "Início"
URL   = "http://192.168.1.127:8080/"
ICON  = "launcher/app/launcher1/TVBrowser.png"
tv = TV()
content = json.dumps({"AppInfo": [{"Title": TITLE, "URL": URL, "Image": ICON, "StoreType": "browser"}]})
print("write ok:", tv.ev("writeFileToNative('launcher/BrowserAppInfo.json'," + json.dumps(content) + ",1)"))
print(tv.ev("chanceAppVersion('add')"))
time.sleep(3)
print("read back:", tv.ev("JSON.stringify(readFileFromNative('launcher/BrowserAppInfo.json',1))"))
