# -*- coding: utf-8 -*-

import json
import os
import urllib
import random
import datetime
import threading
import json
import time
import wsgiref.simple_server
import requests

import bottle
import routing

import xbmcaddon
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs


ADDON = xbmcaddon.Addon()
plugin = routing.Plugin()
app = bottle.Bottle()


cfg_server = ''
cfg_port = 8080
cfg_username = ''
cfg_password = ''
cfg_smb_base = ''
cfg_vote_port = 8081


def load_config():
    global cfg_server
    global cfg_port
    global cfg_username
    global cfg_password
    global cfg_smb_base
    global cfg_vote_port

    cfg_server = ADDON.getSetting('server')
    cfg_port = ADDON.getSetting('port')
    cfg_username = ADDON.getSetting('username')
    cfg_password = ADDON.getSetting('password')
    cfg_smb_base = ADDON.getSetting('smb_base')
    cfg_vote_port = ADDON.getSetting('vote_port')


def load_vote_data():
    path = ADDON.getAddonInfo('profile')
    path = xbmcvfs.translatePath(path)
    path = os.path.join(path, 'votedata.json')
    try:
        with open(path, 'r') as fd:
            data = json.load(fd)
    except:
        data = {}
    return data


def save_vote_data(vote_data):
    path = ADDON.getAddonInfo('profile')
    path = xbmcvfs.translatePath(path)
    path = os.path.join(path, 'votedata.json')
    with open(path, 'w') as fd:
        json.dump(vote_data, fd)


def clear_vote_data():
    save_vote_data({})


def load_movie_data_cache():
    path = ADDON.getAddonInfo('profile')
    path = xbmcvfs.translatePath(path)
    path = os.path.join(path, 'moviedata.json')
    try:
        with open(path, 'r') as fd:
            data = json.load(fd)
    except:
        data = []
    return data


def save_movie_data_cache(movie_data):
    path = ADDON.getAddonInfo('profile')
    path = xbmcvfs.translatePath(path)
    path = os.path.join(path, 'moviedata.json')
    with open(path, 'w') as fd:
        json.dump(movie_data, fd)


def is_movie_data_cache_valid():
    path = ADDON.getAddonInfo('profile')
    path = xbmcvfs.translatePath(path)
    path = os.path.join(path, 'moviedata.json')
    try:
        t1 = os.path.getmtime(path)
        t2 = time.time()
        return (t2 - t1) < (60 * 60 * 1)
    except FileNotFoundError:
        return False


def rpc(method, params={}):
    rpc_req = {'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1}
    r = requests.get('http://{}:{}/jsonrpc'.format(cfg_server, cfg_port), params={'request': json.dumps(rpc_req)}, auth=(cfg_username, cfg_password))
    return r.json()['result']


def get_movies_filtered(filter):
    props = ['file', 'title', 'runtime']
    props += ['genre', 'year', 'rating', 'country']
    props += ['director', 'writer']
    props += ['tagline', 'plot', 'plotoutline']
    props += ['originaltitle', 'sorttitle']
    props += ['fanart', 'thumbnail', 'art']
    r = rpc('VideoLibrary.GetMovies', params={'properties': props, 'filter': filter})
    return r


def conv_image_path(image_path):
    return 'http://{}:{}@{}:{}/image/{}'.format(cfg_username, cfg_password, cfg_server, cfg_port, urllib.parse.quote_plus(image_path))


def conv_image_path_local(image_path, host_name):
    return 'http://{}/image/{}'.format(host_name, urllib.parse.quote_plus(image_path))


def gen_list_item(movie, custom_rating=None):
    info = {'mediatype': 'movie'}
    info['title'] = movie['title']
    info['duration'] = movie['runtime']
    info['genre'] = movie['genre']
    info['year'] = movie['year']
    if custom_rating != None:
        info['rating'] = custom_rating
    else:
        info['rating'] = movie['rating']
    info['country'] = movie['country']
    info['director'] = movie['director']
    info['writer'] = movie['writer']
    info['tagline'] = movie['tagline']
    info['plot'] = movie['plot']
    info['plotoutline'] = movie['plotoutline']
    info['originaltitle'] = movie['originaltitle']
    info['sorttitle'] = movie['sorttitle']

    # Use dateadded to sort by 'random'
    random_date = datetime.datetime.today() + datetime.timedelta(random.random() * 1000)
    info['dateadded'] = random_date.strftime('%Y-%m-%d %H-%M-%S')

    l = xbmcgui.ListItem()
    l.setProperty('IsPlayable', 'true')
    l.setInfo('video', info)
    thumb_path = conv_image_path(movie['thumbnail'])
    fanart_path = conv_image_path(movie['fanart'])
    poster_path = conv_image_path(movie['art']['poster'])
    l.setArt({'thumb': thumb_path, 'fanart': fanart_path, 'poster': poster_path})
    l.setProperty('ServerPath', movie['file'])
    return l


def load_ger_movies():
    if is_movie_data_cache_valid():
        movie_data = load_movie_data_cache()
    else:
        filter = {'or': [
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'DEU'},
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'Deu'},
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'deu'},
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'GER'},
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'Ger'},
            {'field': 'audiolanguage', 'operator': 'is', 'value': 'ger'}
        ]}
        response = get_movies_filtered(filter)
        movie_data = response['movies']
        save_movie_data_cache(movie_data)
    return movie_data


@plugin.route('/')
def index():
    try:
        rpc('JSONRPC.Ping')
    except Exception:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Deutsche Filme (Martin)', 'Server nicht verfübar.')
        return

    movies = load_ger_movies()

    xbmcplugin.setContent(plugin.handle, 'videos')
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(show_voted_info), xbmcgui.ListItem('Kodi Simple Voting System'), isFolder=True)
    for movie in movies:
        smb_path = os.path.join(cfg_smb_base, os.path.split(movie['file'])[1])
        xbmcplugin.addDirectoryItem(plugin.handle, smb_path, gen_list_item(movie))
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(plugin.handle)


def find_movie(movie_data, movie_id):
    for movie in movie_data:
        if movie['movieid'] == movie_id:
            return movie
    return None


def get_unique_movies(vote_data):
    movieids = set()
    for user in vote_data:
        movieids = movieids | vote_data[user].keys()
    return movieids


def filter_by_downvote(movieids, vote_data):
    r = set()
    for movie in movieids:
        skip = False
        for user in vote_data:
            try:
                if vote_data[user][movie] == -1:
                    skip = True
                    break
            except KeyError:
                pass
        if not skip:
            r.add(movie)
    return r


def calc_rating(movieids, vote_data):
    r = {}
    for movie in movieids:
        c = 0
        for user in vote_data:
            try:
                c += vote_data[user][movie]
            except KeyError:
                pass
        r[movie] = min(c, 10)
    return r


@plugin.route('/voted_info')
def show_voted_info():
    vote_data = load_vote_data()
    movie_data = load_ger_movies()

    movieids = get_unique_movies(vote_data)
    movieids = filter_by_downvote(movieids, vote_data)
    movieids = calc_rating(movieids, vote_data)

    xbmcplugin.setContent(plugin.handle, 'videos')
    for movie_id, vote in movieids.items():
        movie = find_movie(movie_data, int(movie_id))
        if movie:
            smb_path = os.path.join(cfg_smb_base, os.path.split(movie['file'])[1])
            xbmcplugin.addDirectoryItem(plugin.handle, smb_path, gen_list_item(movie, int(vote)))
    xbmcplugin.addDirectoryItem(plugin.handle, plugin.url_for(entry_clear_vote_data), xbmcgui.ListItem('-- Wahlergebnis zurücksetzen --'))
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/clear_vote_data')
def entry_clear_vote_data():
    clear_vote_data()
    xbmc.executebuiltin("Container.Refresh")


def run_video_source():
    load_config()
    plugin.run()


class StoppableWSGIRefServer(bottle.ServerAdapter):
    server = None

    def run(self, handler):
        self.server = wsgiref.simple_server.make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


@app.hook('after_request')
def enableCORSAfterRequestHook():
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


def filter_showable_movies(movies, vote_data, username):
    # Get movies, rated by other users
    movieids = get_unique_movies(vote_data)
    movieids = filter_by_downvote(movieids, vote_data)
    try:
        for movie in vote_data[username]:
            try:
                movieids.remove(movie)
            except KeyError as e:
                pass
    except KeyError as e:
        pass

    # Filter movie list by IDs from previous step
    movies = [movie for movie in movies if (str(movie['movieid']) in movieids)]

    return movies


@app.get('/movie')
def service_get_movie():
    username = bottle.request.query.username
    movies = load_ger_movies()
    vote_data = load_vote_data()

    movie = None
    if random.random() < 0.50:
        showable_movies = filter_showable_movies(movies, vote_data, username)
        if len(showable_movies) > 0:
            movie = random.choice(showable_movies)
    
    # If new movie should be displayed, or there are no more showable movies, choose one at random
    if movie is None:
        movie = random.choice(movies)

    movie['thumbnail'] = conv_image_path_local(movie['thumbnail'], bottle.request.headers['host'])
    movie['fanart'] = conv_image_path_local(movie['fanart'], bottle.request.headers['host'])
    for k, v in movie['art'].items():
        movie['art'][k] = conv_image_path_local(v, bottle.request.headers['host'])

    bottle.response.content_type = "application/json"
    return json.dumps(movie)


@app.route('/vote', method=['POST', 'OPTIONS'])
def service_post_vote():
    if bottle.request.method == 'POST':
        # Get data from request
        movieid = str(bottle.request.json['movieid'])
        vote = int(bottle.request.json['vote'])
        username = str(bottle.request.json['username'])

        # Update vote data (create user entry, if not present)
        vote_data = load_vote_data()
        try:
            vote_data[username]
        except KeyError:
            vote_data[username] = {}
        vote_data[username][movieid] = vote
        save_vote_data(vote_data)

        # Update UI in case it's visible
        xbmc.executebuiltin("Container.Refresh")
        return ''
    else:
        return ''


@app.get('/image/<path:path>')
def image_proxy(path):
    if bottle.request.method == 'GET':
        path = 'http://{}:{}@{}:{}/image/{}'.format(cfg_username, cfg_password, cfg_server, cfg_port, urllib.parse.quote_plus(path))
        response = requests.get(path)
        bottle.response.status = response.status_code
        if response.status_code == 200:
            bottle.response.content_type = response.headers.get('content-type')
            return response.content
        else:
            return ''
    else:
        return ''


__server_obj__ = None
__server_thread__ = None


def start_server(port, address):
    global __server_obj__
    __server_obj__ = StoppableWSGIRefServer(host=address, port=port)
    app.run(server=__server_obj__)


def stop_server():
    global __server_obj__
    global __server_thread__

    if __server_obj__:
        __server_obj__.stop()

    if __server_thread__:
        __server_thread__.join()

    __server_obj__ = None
    __server_thread__ = None


def run_service():
    load_config()

    global __server_thread__
    __server_thread__ = threading.Thread(target=start_server, args=(cfg_vote_port, ''))
    __server_thread__.start()

    monitor = xbmc.Monitor()
    monitor.waitForAbort()

    stop_server()
