# -*- coding: utf-8 -*-

import re
import serial


class TvControl(object):
    # Get Power     "ka 00 FF\r"
    # Off           "ka 00 00\r"
    # On            "ka 00 01\r"
    # Get Input     "xb 00 FF\r"
    # Input HDMI1   "xb 00 90\r"
    # Input HDMI2   "xb 00 91\r"
    # Input HDMI3   "xb 00 92\r"
    # Input AV2     "xb 00 21\r"

    INPUT_NONE = None
    INPUT_HDMI1 = 0x90
    INPUT_HDMI2 = 0x91
    INPUT_HDMI3 = 0x92
    INPUT_AV2 = 0x21

    def __init__(self, tty_dev='/dev/ttyUSB0'):
        self.ser = serial.Serial(tty_dev, timeout=1.0)

    def __deinit__(self):
        self.ser.close()

    def power_get(self):
        self.ser.write(b'ka 00 FF\r')
        data = self.ser.read(10)
        match = re.match(b'a 01 OK01x\Z', data)
        if match:
            return True
        else:
            return False

    def power_off(self):
        self.ser.write(b'ka 00 00\r')

    def power_on(self):
        self.ser.write(b'ka 00 01\r')

    def input_get(self):
        self.ser.write(b'xb 00 FF\r')
        data = self.ser.read(10)
        match = re.match(b'b 01 OK([0-9A-Fa-f]{2})x\Z', data)
        if match:
            return int(match.group(1), 16)
        else:
            return None

    def input_set(self, input):
        cmd = 'xb 00 {:02X}\r'.format(input).encode('utf8')
        self.ser.write(cmd)
