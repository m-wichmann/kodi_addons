import xbmc
import xbmcgui
import xbmcaddon

def log(msg):
    xbmc.log(msg=msg, level=xbmc.LOGWARNING)



addon = xbmcaddon.Addon('script.service.hyperion')

is_enabled = addon.getSetting('hyperion_enable').lower() == 'true'
addon.setSetting('hyperion_enable', str(not is_enabled))

if is_enabled:
  note_str = 'Service disabled.'
else:
  note_str = 'Service enabled.'

dialog = xbmcgui.Dialog()
dialog.notification(addon.getAddonInfo('name'), note_str, addon.getAddonInfo('icon'))
