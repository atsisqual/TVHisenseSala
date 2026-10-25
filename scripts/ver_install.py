"""SÓ LEITURA. Vê se a página do launcher tem as funções de instalação de apps (Hisense_installApp, ...)."""
from _cdp import TV
tv = TV()
for n in ["Hisense_installApp", "Hisense_uninstallApp", "refreshAppsOnHisenseUI", "Hisense_GetModelName",
          "Hisense_GetFirmWareVersion", "Hisense_GetDeviceID"]:
    print(n, "->", tv.ev("typeof " + n))
print("Hisense.* ->", tv.ev("(function(){var a=[];for(var k in Hisense)a.push(k);return a.join(',')})()"))
print("window Hisense_* ->", tv.ev("Object.getOwnPropertyNames(window).filter(function(k){return /^Hisense/i.test(k)}).join(',')"))
