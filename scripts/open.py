"""Abre uma app da TV: python open.py YOUTUBE | NETFLIX | DAILYMOTION | ACCUWEATHER | GAMECENTER | TVBROWSER"""
import sys
from _cdp import TV
app = sys.argv[1] if len(sys.argv) > 1 else "YOUTUBE"
print(TV().ev("UI.popAllModule(); startThirdPartyApp(APPNAME.%s, APPNAME.%s, CMDType.NATIVEAPP, CMDMethod.MENU, false);" % (app, app)))
