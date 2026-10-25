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
- Menu Android TV (scripts/menu.py): as teclas já funcionam; falta confirmar que o OK abre as apps. `scripts/keepalive.py` volta a injetá-lo se a TV reiniciar.
- Scrape do launcher feito no telemóvel (`~/tvdump/`, 51 scripts). Ficheiros maiores: `mainTiles.js` 161 KB, `launcherDataInterface.js` 123 KB, `UI.js` 145 KB.
- Próximo passo: ler `mainTiles.js`, `allApps.js` e `UI.js` para ver como o ecrã de apps é desenhado e como ligar o menu sem tapar o launcher.

## Alternativa permanente
Box Android/Google TV no HDMI (Chromecast com Google TV, Xiaomi TV Stick, Fire TV Stick): único caminho para um launcher Android TV a sério.

## Leitura do código do launcher (25-10-2026, a partir do scrape)
- `Hisense.File` tem: read, write, exists, delete, move, readCacheIndex, cache, downloadAsync. (Não verificado se aceita caminhos fora da pasta de trabalho do launcher.)
- `downloadAsync`/`cache` servem para os ícones: `getLocalAppImgUrl` troca um URL de imagem por uma cópia local; se não existir, usa o URL e põe-no na lista `launcherNeedDownLoadAppImgUrl` para descarregar. Por isso o ícone de um mosaico em `BrowserAppInfo.json` tem de ser um URL de imagem que exista.
- `mainTiles.js` (161 KB): o ecrã inicial usa `launcherTiles.initSequence`; há modo de edição (`launcher.isEditMode`), alvo de adição (`launcher.Adtarget`) e submódulo `UI.pushSubModule("launcher","allApps",true)` (linha ~1646). Hipótese (por confirmar): o caminho oficial para pôr um mosaico na fila do ecrã inicial é o modo de edição + "adicionar app", guardado por `setRememberEditAppToNativeFile`.
- `sdk/UI.js`: `UI.dispatchKeyEvent` na linha 2623, chamada a partir das linhas 410, 2526, 2541, 2616; `UI.processKey` na linha 1840.

## Extração em bruto (decisão do utilizador: preferir dados completos a grep em pedaços)
- `scripts/dump_all.py` (autónomo, só leitura): percorre `/opt/hisenseUI/`, lê os ficheiros de dados do launcher e grava o estado em memória; junta tudo em `~/tvdump_raw.tar.gz` no telemóvel. Enviar esse ficheiro à conversa para análise completa.
- Por confirmar com os dados: como se entra no modo de edição do ecrã inicial (`toEditMode`, `mainTiles.js`) e onde `setRememberEditAppToNativeFile` (`lib/launcherDataInterface.js:1608`) grava a ordem dos mosaicos.


## Resultados do dump em bruto (tvdump_raw.tar.gz, 25-10-2026)
- A pasta `/opt/hisenseUI/` tem 4244 ficheiros: `html/` (a interface, ~4179), `opera_dir`, `opera_home`, `appdata`, `bin` e os scripts de arranque (`startgui.sh`, `hisenseUI_env.sh`). A interface corre num browser Opera (SDK de dispositivos), por isso há DevTools na 9223.
- **Os mosaicos do ecrã inicial vivem em `launcher/rememberEditApp.json`** (workRoot 1), formato `{"countryCode":"PRT","appInfo":[{Name,Icon,url,cmd,data:{appimg,canMove,canRemove,img,storeType,txt,url,urlType}}]}`. Escreve-o `setRememberEditAppToNativeFile`, o mesmo que o modo de edição da TV usa. Linha do utilizador no momento do dump: Search, Apps, **Teste** (resto do nosso teste, aponta para example.com), Inputs, Media, Settings.
- Um mosaico personalizado é uma entrada `cmd:14` com `data.url`, `data.urlType` (36=web, 37=app nativa) e `data.storeType`. Ao carregar OK, o launcher chama `startThirdPartyApp(null, url, urlType, CMDMethod.MENU, false, 0xFFFFFF, nome, storeType)`.
- `BrowserAppInfo.json` deixou de existir depois de o mosaico ser integrado; só é apagado se estiver mal formado ou ao remover o mosaico.
- **No ecrã inicial, com um mosaico focado: UP = modo de mover, DOWN = modo de editar** (`launcherTiles.onkey_UP/DOWN` em `mainTiles.js`).
- `opera.json` indica um diretório `userjs` em `/opt/hisenseUI/opera_dir/userjs` (scripts carregados pelo browser) que NÃO existe no dump; não sabemos se a pasta é gravável.
- Cadeias de arranque comentadas em `startgui.sh` mencionam `/3rd_rw/` (atualização do launcher por pacote). Não explorado: risco alto de bloquear a TV.
- Persistência: `rememberEditApp.json` é o ficheiro que o próprio utilizador altera ao editar o ecrã inicial, por isso deve sobreviver a reinícios (por confirmar depois de um reinício).

## Onde ficam os dados do launcher (25-10-2026, em investigação)
- `descobrir_raiz.py` deu falsos positivos: o browser devolve `""` (0 bytes) para ficheiros inexistentes em `file://`. Não usar o tamanho para detetar existência; usar o nome na listagem de diretório (`procurar_raiz.py`).
- Ficou claro que o browser consegue listar o sistema de ficheiros inteiro por `file://` (`/`, `/var/local/`, ...). `/3rd_rw/` não é listável.
- `/var/local/hisenseUI/` só contém `opera_home` → os ficheiros de `workRoot 1` NÃO estão aí.
- `/var/local/applications/` existe; o launcher abre páginas HTML locais daí (`E_MANUAL`: `file:///var/local/applications/Local_ebook/Ebook_<lang>/index.html`, CMDType.HISENSEPAGE). Ideia: se a pasta de `workRoot 1` for legível por `file://`, gravar lá uma página e abri-la como mosaico.

## workRoot 1 localizado (25-10-2026)
- `rAppVersion` está em `/var/local/applications/UI/` (pasta com hiAvsService, hisenseUI, launcher, notify, weather, deviceId, ...). Logo workRoot 1 = `/var/local/applications/UI/` (inferido). Legível por `file://`.
- `/var/local/applications/` tem: channel, emanual, eula, Local_ebook, UI.
- O launcher abre páginas locais com `startThirdPartyApp(APPNAME.E_MANUAL, "file:///...", CMDType.HISENSEPAGE, CMDMethod.COMMANDURL, false)` (`SettingAboutEntry.js:308`).
- Por testar: `scripts/listar_ui.py` (só leitura) e `scripts/teste_escrita.py` (grava/abre/apaga um ficheiro de teste). Se a escrita e a abertura funcionarem, o menu Android TV pode ficar como página guardada na TV + mosaico cmd 14.
- Escrita em workRoot 1 FUNCIONA (`Hisense.File.write(f,html,1)` -> 0; lê-se por file://). Abrir por `E_MANUAL`+HISENSEPAGE funciona à 1.ª vez mas depois NÃO recarrega: se a app é a "app atual", `startThirdPartyApp` só faz `focusCurrentApp()` (PubFunc.js ~5318). Usar `APPNAME.THIRDPARTY` (="opera4x") com `appParam` próprio e `StoreType.HISENSE` (99) -> `:am,opera4x,:resume=[-s,hisense,-u,URL]`.
- A página aberta corre fora do DevTools (só há o alvo `UI`), por isso o diagnóstico é feito no próprio ecrã (`teste_diag.py`).
- Diagnóstico da página guardada (foto, 25-10-2026): `window.opener` é `null` (sem acesso a UI/startThirdPartyApp/APPNAME), `Hisense` existe mas sem chaves enumeráveis, e **as teclas do comando não chegam à página** (nenhum evento keydown/keyup/keypress). Conclusão: uma página HTML guardada na TV não serve de menu navegável por teclas nem abre apps nativas. Ficheiros de teste na TV: `teste_tvmenu.html`, `teste_diag.html`, `teste_diag2.html` (workRoot 1) — apagar com `Hisense.File.delete(nome,1)`.
- Hipótese por testar (risco médio): persistência por User JS do Opera via `/var/local/hisenseUI/opera_home` (graável?) — não tentada.

## Projetos existentes (pesquisa 25-10-2026)
- Método comum: **instalar uma web app como app real da TV** (aparece em "My Apps" e persiste, aponta para um URL HTML5). Três vias: (1) `hisense://debug` no Browser da TV (formulário Nome + URL; TVs antigas, [microimpuls](https://microimpuls.com/en/docs/smarty/extra/hisense-vidaa-debug-guide)); (2) DNS spoof de `vidaahub.com` + `Hisense_installApp(nome, nome_debug, icon, ..., URL, 'store', cb)` ([trialuser/vidaa-appstore](https://github.com/trialuser/vidaa-appstore), [Stremio/stremio-hisense-install](https://github.com/Stremio/stremio-hisense-install), [arashbehmand/vidaa-custom-app](https://github.com/arashbehmand/vidaa-custom-app)); (3) MQTT 36669 com PIN, modelos recentes ([gridoe/Sidee](https://github.com/gridoe/Sidee), [Zfinix/vidaa-launcher](https://github.com/Zfinix/vidaa-launcher)).
- [chrisns/hisense_vidaa](https://github.com/chrisns/hisense_vidaa) usa a mesma porta 9223 sem auth (TV 2016, OMI/4.7): `Runtime.evaluate`, `changeSourceTo(uid)`, `model.source.*`, `model.video.*`.
- Nenhum projeto muda o ecrã inicial: o do Zfinix diz que o VIDAA não permite substituí-lo (usa um watcher que abre a página quando a TV está no início).
- Por testar na A6100 (U2.5): `hisense://debug` no Browser e `scripts/ver_install.py`.

## Apps instaladas por `hisense://debug` (25-10-2026) — descoberta chave
- No Browser da TV, `hisense://debug` abre o formulário (App Name, Thumbnail, IconSmall, IconLarge, App Url, INSTALL). **O URL tem de começar por http/https** (file:// recusado).
- A app instalada ("Teste", `http://192.168.1.127:8099/d.html`) aparece na lista de apps e **recebe as teclas do comando** (keydown/keyup 38/40, ArrowUp/ArrowDown). `opener` é null, `Hisense` vazio, sem UI/startThirdPartyApp.
- Ideia em teste: a página fala com `ws://192.168.1.85:9223` (DevTools) para pedir ao launcher que abra as apps nativas. Pode falhar por CORS no `/json` (precisa do UUID da página). Falta decidir onde alojar a página de forma permanente (GitHub Pages por https? certificados antigos na TV).

## Menu premium + jogos (25-10-2026)
- `pagina/menu.html` é a app instalada (App Url http://<host>/menu.html via `hisense://debug`, ou `scripts/abrir_url.py` por CDP, sem usar o comando da TV). Abre apps nativas chamando `Runtime.evaluate` no DevTools da própria TV (`http://192.168.1.85:9223/json` → WebSocket), sem CORS. Configuração no topo do ficheiro (TILES, CIDADE, TV).
- Versão leve para a TV (sem transições de opacidade/sombra grandes): a A6100 engasga com fades em ecrã inteiro.
- Tempo: open-meteo (https com fallback http), Vila Nova de Famalicão (41.41, -8.52); cache em localStorage. Por confirmar que a TV aceita o certificado.
- Jogos em `pagina/jogos/` (2048 MIT, Hextris GPL-3.0) num iframe do mesmo host; OK/amarelo ligados a começar/reiniciar; Back e botões coloridos fecham o jogo (códigos do Back por confirmar na TV).
- Pendente: alojar `pagina/` fora do telemóvel (GitHub Pages por https? certificados da TV), gravar a app de forma definitiva, remover o mosaico "Teste" e os ficheiros de teste da TV.
