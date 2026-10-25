"""Apaga o ficheiro dos mosaicos adicionados."""
from _cdp import TV
print(TV().ev("deleteNativeFile('launcher/BrowserAppInfo.json',1);chanceAppVersion('undo');'ok'"))
