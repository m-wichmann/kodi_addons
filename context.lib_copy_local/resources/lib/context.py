# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import sys
import os
import time
import requests
import json

ADDON = xbmcaddon.Addon()

cfg_server = ADDON.getSetting('server')
cfg_port = ADDON.getSetting('port')
cfg_username = ADDON.getSetting('username')
cfg_password = ADDON.getSetting('password')
cfg_dest_base = ADDON.getSetting('dest_base')


def rpc(method, params={}):
    rpc_req = {'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1}
    r = requests.get('http://{}:{}/jsonrpc'.format(cfg_server, cfg_port), params={'request': json.dumps(rpc_req)}, auth=(cfg_username, cfg_password))
    return r.json()['result']


def download_file(in_path, out_path):
    r = rpc('Files.PrepareDownload', {'path': in_path})
    dl_path = r['details']['path']

    r = requests.get('http://{}:{}/{}'.format(cfg_server, cfg_port, dl_path), auth=(cfg_username, cfg_password), stream=True)

    if r.status_code == 200:
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create('Kopiere nach lokal', os.path.split(in_path)[1])

        exp_file_size = int(r.headers['content-length'])
        sum_file_size = 0
        with open(out_path, 'wb') as fd:
            for chunk in r.iter_content(65536):
                fd.write(chunk)
                sum_file_size += len(chunk)
                pDialog.update(int(float(sum_file_size) / float(exp_file_size) * 100.0))


def run():
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')

    in_path = sys.listitem.getProperty('ServerPath')
    out_path = os.path.join(cfg_dest_base, os.path.split(in_path)[1])

    download_file(in_path, out_path)
