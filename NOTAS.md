# Notas do projeto — TV Hisense da sala

Memória do projeto: o que sabemos, o que funciona, o que correu mal. Atualizar sempre que houver novidades.

## A TV
- Hisense HE65A6100UWTS (série A6100, 2018), VIDAA U2.5, firmware VA001.01.00a.J0819.
- Não é Android TV: não há ADB, por isso CleanYourTV e afins não servem.
- IP na rede de casa: 192.168.1.85 (convém fixar no router). Telemóvel (Termux): 192.168.1.127.

## Objetivo
Dar à TV um menu de apps com aspeto Android TV, e poder adicionar atalhos. Não é para remover mosaicos.

## Descobertas
- Scan nmap: sem telnet/SSH/ADB. A porta **9223** é um DevTools do Chromium (Chrome 53, "OMI/4.9"), **sem autenticação**. A página inspecionável é o próprio launcher: `file:///opt/hisenseUI/html/hisenseUI/index.html`.
- O launcher é uma app HTML desenhada num canvas (pixi.js). Código em `/opt/hisenseUI/html/hisenseUI/` (provavelmente só de leitura).
- Ficheiros de dados graváveis através de `writeFileToNative(path, content, 1)`:
  - `launcher/preset.txt` — lista de mosaicos de fábrica (17).
  - `launcher/BrowserAppInfo.json` — mosaicos adicionados pelo utilizador (`{"AppInfo":[{"Title","URL","Image","StoreType":"browser"}]}`). Funciona: o mosaico aparece na lista de Apps, mas não no ecrã inicial.
  - `launcher/deletedPresetApp.txt` — mosaicos removidos.
- Lançar apps: `UI.popAllModule(); startThirdPartyApp(APPNAME.X, APPNAME.X, CMDType.NATIVEAPP, CMDMethod.MENU, false)`. Confirmado com YouTube.
  - APPNAME: netflix, youtube, dailymotion, accuweather, gamecenter, browser, ...
  - CMDType: NATIVEAPP=37, WEBAPP=36, BROWSER=40. CMDMethod: REMOTECONTROL=1, MENU=3.
- **Teclas**: não chegam ao browser (não há eventos DOM). Passam por `UI.receiveKey` → `UI.dispatchKeyEvent(código)`. Códigos: 37 esquerda, 39 direita, 13 OK, 405 amarelo, 38/40 cima/baixo.
- **Ecrãs do módulo `launcher`**: o menu de fontes e o menu Smart são ambos `UI.getCurrModule().name == 'launcher'`. Distinguem-se por `launcher.children[3]`: `allInputs` (fontes) vs `allApps` (Smart).
- Mosaicos web: o browser da TV não confia em muitos certificados HTTPS (lista de 2018). Preferir páginas `http://` na rede local.
- Navegar na página-início pelo TV Browser usa o cursor do comando, não as setas.

## O que correu mal (não repetir)
- Menu injetado a testar só `UI.getCurrModule().name == 'launcher'`: apareceu também no menu de fontes. Usar a deteção `children[3] == allApps`.
- Substituir `UI.dispatchKeyEvent` sem deixar passar as teclas desconhecidas: a TV ficou sem responder ao comando (também ao de ligar/desligar). Recuperou com `off.py` (repõe a função original).
- Regra: nunca fazer uma captura de teclas sem ter à mão o `off.py` e sem deixar passar todas as teclas que não são do menu.
- Tudo o que é injetado fica só em memória; um reinício (ou `reload.py`) apaga. A única coisa persistente foi o mosaico "Início" (`BrowserAppInfo.json`).

## Estado atual (25-10-2026)
- Menu Android TV (scripts/menu.py): as teclas já funcionam; falta confirmar que o OK abre as apps.
- Scrape do launcher feito no telemóvel (`~/tvdump/`, 51 scripts). Ficheiros maiores: `mainTiles.js` 161 KB, `launcherDataInterface.js` 123 KB, `UI.js` 145 KB.
- Próximo passo: ler `mainTiles.js`, `allApps.js` e `UI.js` para ver como o ecrã de apps é desenhado e como ligar o menu sem tapar o launcher.

## Alternativa permanente
Box Android/Google TV no HDMI (Chromecast com Google TV, Xiaomi TV Stick, Fire TV Stick): único caminho para um launcher Android TV a sério.

## Leitura do código do launcher (25-10-2026, a partir do scrape)
- `Hisense.File` tem: read, write, exists, delete, move, readCacheIndex, cache, downloadAsync. (Não verificado se aceita caminhos fora da pasta de trabalho do launcher.)
- `downloadAsync`/`cache` servem para os ícones: `getLocalAppImgUrl` troca um URL de imagem por uma cópia local; se não existir, usa o URL e põe-no na lista `launcherNeedDownLoadAppImgUrl` para descarregar. Por isso o ícone de um mosaico em `BrowserAppInfo.json` tem de ser um URL de imagem que exista.
- `mainTiles.js` (161 KB): o ecrã inicial usa `launcherTiles.initSequence`; há modo de edição (`launcher.isEditMode`), alvo de adição (`launcher.Adtarget`) e submódulo `UI.pushSubModule("launcher","allApps",true)` (linha ~1646). Hipótese (por confirmar): o caminho oficial para pôr um mosaico na fila do ecrã inicial é o modo de edição + "adicionar app", guardado por `setRememberEditAppToNativeFile`.
- `sdk/UI.js`: `UI.dispatchKeyEvent` na linha 2623, chamada a partir das linhas 410, 2526, 2541, 2616; `UI.processKey` na linha 1840.
