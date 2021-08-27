
import xbmc
import xbmcaddon
import xbmcgui
import os
import traceback

# Add the library path before loading Hyperion
__addon__      = xbmcaddon.Addon()
__cwd__        = __addon__.getAddonInfo('path')
sys.path.append(xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')))

from hyperion.Hyperion import Hyperion

HYPERION_IP = '127.0.0.1'
HYPERION_PORT = 19445
HYPERION_WIDTH = 64
HYPERION_HEIGHT = 64
HYPERION_PRIORITY = 150

enabled = False


def log(msg):
    '''Write a debug message to the Kodi log
    '''
    addon = xbmcaddon.Addon()
    xbmc.log("### [%s] - %s" % (addon.getAddonInfo('name'),msg,), level=xbmc.LOGERROR)

def notify(msg):
    '''Show a notification in Kodi
    '''
    addon = xbmcaddon.Addon()
    xbmcgui.Dialog().notification(addon.getAddonInfo('name'), msg, addon.getAddonInfo('icon'))

def load_settings():
    global enabled
    addon = xbmcaddon.Addon()
    enabled = addon.getSetting("hyperion_enable").lower() == 'true'

class MyMonitor (xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        load_settings()


if  __name__ == "__main__":
    load_settings()

    monitor = MyMonitor()
    player = xbmc.Player()

    capture = xbmc.RenderCapture()
    capture.capture(HYPERION_WIDTH, HYPERION_HEIGHT)
    hyperion = Hyperion(HYPERION_IP, HYPERION_PORT)

    while not monitor.abortRequested():
        try:
            if enabled and player.isPlayingVideo():
                data = capture.getImage()
                if len(data) == 0:
                    capture.capture(HYPERION_WIDTH, HYPERION_HEIGHT)
                    hyperion.clear(HYPERION_PRIORITY)
                    continue

                if capture.getImageFormat() == 'ARGB':
                    del data[0::4]
                elif capture.getImageFormat() == 'BGRA':
                    del data[3::4]
                    data[0::3], data[2::3] = data[2::3], data[0::3]

                hyperion.sendImage(capture.getWidth(), capture.getHeight(), bytes(data), HYPERION_PRIORITY, -1)
            else:
                hyperion.clear(HYPERION_PRIORITY)
                monitor.waitForAbort(1.0)
        except Exception as e:
            notify('Something went wrong')
            log(e)
            log("".join(traceback.format_exception(type(e), e, e.__traceback__)))
            hyperion.clear(HYPERION_PRIORITY)
            monitor.waitForAbort(30.0)
            if not monitor.abortRequested():
                capture = xbmc.RenderCapture()
                capture.capture(HYPERION_WIDTH, HYPERION_HEIGHT)
                hyperion = Hyperion(HYPERION_IP, HYPERION_PORT)

        monitor.waitForAbort(0.010)
