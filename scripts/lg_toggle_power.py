# -*- coding: utf-8 -*-

import time
from lg_ctrl import TvControl

tv = TvControl(tty_dev='/dev/ttyLG')

is_on = tv.power_get()

if is_on:
    for i in range(5):
        tv.power_off()
        time.sleep(0.1)
else:
    for i in range(5):
        tv.power_on()
        time.sleep(0.1)
