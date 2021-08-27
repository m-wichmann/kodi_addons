# -*- coding: utf-8 -*-

import xbmcgui
from lg_ctrl import TvControl

tv = TvControl(tty_dev='/dev/ttyLG')

curr_input = tv.input_get()

if curr_input is None:
    xbmcgui.Dialog().notification('Input Select', 'Konnte aktuellen Input nicht ermitteln', xbmcgui.NOTIFICATION_ERROR)
elif curr_input == TvControl.INPUT_HDMI1:
    ret =  xbmcgui.Dialog().select('Bitte TV-Input wählen', ['Playstation 2', 'Playstation 3', 'Playstation 4'])
    if ret == 0:
        target_input = TvControl.INPUT_AV2
    elif ret == 1:
        target_input = TvControl.INPUT_HDMI2
    elif ret == 2:
        target_input = TvControl.INPUT_HDMI3
    tv.input_set(target_input)
else:
    tv.input_set(TvControl.INPUT_HDMI1)
