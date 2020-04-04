#!/usr/bin/env python

import miniupnpc
import socket
from uuid import uuid1
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape

import bubbob.bb, gamesrv
import external_tools

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)
define("level", default='CompactLevels.py', type=str,
       help="Levels to play (can also be changed before the game starts)")
define("metaserver", default="buildbot.pypy.org:8888", type=str,
       help="Metaserver to use, or 'none'")
define("upnp", default=True, type=bool, help='Whether to open the port via UPNP when launching.')
define("hostname", default=None, type=str,
       help="Nickname published on the metaserver")


class Application(tornado.web.Application):
    metaserver_url = None

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/gamesocket", GameSocketHandler),
            (r"/dynamic/([0-9a-f]+)", DynamicHandler),
            (r"/cheat/(.+)", CheatHandler),
            (r"favicon.ico", FavIconHandler),
        ]
        super(Application, self).__init__(handlers, static_path="static")
        self.periodic_callback = tornado.ioloop.PeriodicCallback(
            self.invoke_periodic_callback, 25)
        self.periodic_callback_is_running = False
        self.metaserver_key = uuid1()
        self.prepare_metaserver_connection()

    def updated_client_list(self):
        if len(gamesrv.clients) == 0:
            if self.periodic_callback_is_running:
                print("no more client, pausing")
                self.periodic_callback.stop()
                self.periodic_callback_is_running = False
        else:
            if not self.periodic_callback_is_running:
                print("starting periodic callback")
                self.periodic_callback.start()
                self.periodic_callback_is_running = True
        return self.periodic_callback_is_running

    def invoke_periodic_callback(self):
        try:
            r = gamesrv.game.mainstep()
        except:
            import pdb, sys
            pdb.post_mortem(sys.exc_info()[2])
            raise
        if r > 0:
            msg = u''.join(gamesrv.sprites)
            for client in gamesrv.clients:
                client.gs_update_drawing(msg)

    def prepare_metaserver_connection(self):
        if options.metaserver.lower() in ('','none','0','off','no','false'):
            return
        self.metaserver_url = 'http://%s/' % (options.metaserver,)

        def notify_metaserver(**query):
            query['d'] = gamesrv.game.FnDesc
            query['e'] = gamesrv.game.FnExtraDesc()
            message = tornado.escape.json_encode(query)
            self.metaserver_websocket.write_message(message)

        def metaserver_ready(websocket, *args):
            self.metaserver_websocket = websocket.result()
            hostname = options.hostname or socket.getfqdn()
            notify_metaserver(h=hostname, p=options.port)
            gamesrv.game.updatemetaserver = notify_metaserver

        tornado.websocket.websocket_connect(
            'ws://%s/bub-n-bros-game-stat' % (options.metaserver,),
            callback=metaserver_ready)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class DynamicHandler(tornado.web.RequestHandler):
    def get(self, filename):
        bmp = gamesrv.bitmaps['dynamic', filename]
        if not hasattr(bmp, '_png_version'):
            bmp._png_version = external_tools.convert_ppm_to_png(
                bmp.read(), bmp.colorkey)
        self.set_header('Content-Type', 'image/png')
        self.set_header('Cache-Control', 'max-age=8640000')
        self.write(bmp._png_version)


class GameSocketHandler(tornado.websocket.WebSocketHandler):
    gs_closed = False
    gs_app = None
    gs_prev_drawing = u''
    gs_prev_change_levels = None
    gs_prev_board_size = None

    def __init__(self, *args, **kwds):
        super(GameSocketHandler, self).__init__(*args, **kwds)
        self.gs_players = {}

    def gs_update_drawing(self, drawing):
        prev_drawing = self.gs_prev_drawing
        self.gs_prev_drawing = drawing
        i = 0
        for i in range(min(len(prev_drawing), len(drawing), 0xC000)):
            if drawing[i] != prev_drawing[i]:
                break
        msg = u'D' + chr(i + 1) + drawing[i:]
        self.write_message(msg)
        self.update_changelevels()

    def gs_static_url(self, filename, ext, external_static_url=None):
        if '.' in filename:
            filename = filename[:filename.index('.')] + ext
            if external_static_url is None:
                return self.static_url(filename)
            else:
                return external_static_url % (filename,)
        else:
            return '/dynamic/' + filename

    def gs_send_definition(self, datachunk):
        filename = datachunk.filename
        url = self.gs_static_url(filename, '.png')
        self.write_message(datachunk._msgdef % (url,))

    def gs_define_keys(self):
        for keyname, icolist, fn in gamesrv.game.FnKeys:
            msg = ["def_key", keyname]
            for ico in icolist:
                msg.append(str(ico.code))
            self.write_message('`'.join(msg))

    def gs_start_music(self):
        music_url = (
            'http://bytebucket.org/arigo/bub-n-bros/raw/default/static/%s')
        music = ["music", str(gamesrv.currentmusics[0])]
        for m in gamesrv.currentmusics[1:]:
            music.append(self.gs_static_url(m.filename, '.ogg', music_url))
            music.append(self.gs_static_url(m.filename, '.mp3', music_url))
        self.write_message('`'.join(music))

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def gs_possibly_resend_init(self):
        board_size = (gamesrv.game.width, gamesrv.game.height)
        if board_size != self.gs_prev_board_size:
            self.gs_prev_board_size = board_size
            self.write_message("init`%d`%d" % board_size)

    def open(self):
        print("opening connexion")
        self.gs_possibly_resend_init()
        for bitmap in gamesrv.bitmaps.values():
            for icon in bitmap.icons.values():
                self.gs_send_definition(icon)
        self.gs_define_keys()
        for player_id, p in gamesrv.game.FnPlayers().items():
            if p.standardplayericon is not None:
                self.write_message("player_icon`%d`%d" % (
                    player_id, p.standardplayericon.code))
        gamesrv.clients.append(self)
        self.gs_start_music()
        self.gs_app.updated_client_list()

    def on_close(self):
        print("closing connexion")
        gamesrv.clients.remove(self)
        self.gs_closed = True
        for p in self.gs_players.values():
            p._playerleaves()
        if not gamesrv.clients and gamesrv.game is not None:
            gamesrv.game.FnDisconnected()
        self.gs_app.updated_client_list()

    def on_message(self, message):
        message = message.split('`')
        getattr(self, 'gs_cmsg_' + message[0])(*message[1:])

    def gs_cmsg_add_player(self, id):
        id = int(id)
        if id in self.gs_players:
            print("Note: player %d is already playing" % (id,))
            return
        p = gamesrv.game.FnPlayers()[id]
        if p is None:
            print("Too many players. New player %d refused." % (id,))
            self.write_message("player_kill`%d" % id)
            return
        if p.isplaying():
            print("Note: player %d is already played by another client" % (id,))
            return
        print("New player %d" % (id,))
        p._client = self
        p.playerjoin()
        p.setplayername('')
        self.gs_players[id] = p
        gamesrv.game.updateplayers()
        for client in gamesrv.clients:
            client.write_message("player_join`%d`%d" % (id, client is self))

    def gs_cmsg_remove_player(self, id):
        id = int(id)
        try:
            p = self.gs_players[id]
        except KeyError:
            print("Note: player %d is not playing" % (id,))
        else:
            p._playerleaves()

    def gs_killplayer(self, player):
        for id, p in list(self.gs_players.items()):
            if p is player:
                if not self.gs_closed:
                    self.write_message("player_kill`%d" % id)
                del self.gs_players[id]
                if gamesrv.game:
                    gamesrv.game.updateplayers()

    def gs_play_sound(self, filename):
        ssnd1 = self.gs_static_url(filename, '.ogg')
        ssnd2 = self.gs_static_url(filename, '.mp3')
        self.write_message("play`%s`%s" % (ssnd1, ssnd2))

    def gs_cmsg_key(self, player_id, keynum):
        player_id = int(player_id)
        keynum = int(keynum)
        if gamesrv.game is not None:
            try:
                player = self.gs_players[player_id]
                fn = gamesrv.game.FnKeys[keynum][2]
            except (KeyError, IndexError):
                gamesrv.game.FnUnknown()
            else:
                getattr(player, fn) ()

    def update_changelevels(self):
        levels = gamesrv.game.FnChangeLevels
        if levels == self.gs_prev_change_levels:
            return
        self.gs_prev_change_levels = levels
        if levels:
            msg = []
            for lvlfilename in levels:
                name = lvlfilename.split('.')[0]
                name = ('<a href="javascript:changelevels(\'%s\')">%s</a>'
                        % (lvlfilename, name))
                if ('levels/' + lvlfilename) == gamesrv.game.levelfile:
                    name = '&lt;%s&gt;' % name
                msg.append(name)
            msg = '&nbsp; &nbsp;'.join(msg)
            msg = ('<br><br>Reload level set:&nbsp; &nbsp;'
                   '<strong>' + msg + '</strong>')
            if self.gs_app is not None and self.gs_app.metaserver_url:
                msg += '\n<br><br>\n<a href="%s">Visit the metaserver</a>' % (
                    self.gs_app.metaserver_url,)
        else:
            msg = ''
        self.write_message("changelevels`%s" % msg)

    def gs_cmsg_change_levels(self, lvl):
        lvl = lvl.encode('utf-8')
        levels = gamesrv.game.FnChangeLevels
        if levels and lvl in levels:
            gamesrv.game.levelfile = 'levels/' + lvl
            gamesrv.game.reset()
            for client in gamesrv.clients:
                client.gs_prev_change_levels = 'reload!'
            for client in gamesrv.clients:
                client.gs_possibly_resend_init()


class CheatHandler(tornado.web.RequestHandler):
    def get(self, bonusname):
        gamesrv.game.cheat(bonusname)

class FavIconHandler(tornado.web.RequestHandler):
    def get(self):
        with open('static/favicon.ico', 'rb') as f:
            self.write(f.read())


def main():
    tornado.options.parse_command_line()
    if not options.level:
        raise Exception("use --level=LEVEL.bin or --level=LEVEL.py")
    bubbob.bb.BubBobGame('levels/' + options.level)
    app = Application()
    app.listen(options.port)

    if options.upnp:
        print('Opening port %s via UPNP...' % options.port)
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 10
        upnp.discover()
        upnp.selectigd()
        upnp.addportmapping(options.port, 'TCP', upnp.lanaddr, options.port, 'BubNBros', '')

    print('Starting game server...')
    GameSocketHandler.gs_app = app
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
