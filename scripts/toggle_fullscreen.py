import xbmc
import xbmcgui

WINDOW_FULLSCREEN_VIDEO = 12005

if xbmc.getCondVisibility('Player.HasMedia'):
    if xbmcgui.getCurrentWindowId() == WINDOW_FULLSCREEN_VIDEO:
        xbmc.executebuiltin('Action(PreviousMenu)')
    else:
        xbmc.executebuiltin('ActivateWindow(fullscreenvideo)')
