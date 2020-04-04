#!/usr/bin/env python

import os, time, random, datetime
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

ICON_DIR = 'static/icons'
ICONS = [_s for _s in os.listdir(ICON_DIR) if _s.endswith('.png')]
assert ICONS


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/client", ClientHandler),
            (r"/bub-n-bros-game-stat", GameStatHandler),
            (r"favicon.ico", FavIconHandler),
        ]
        super(Application, self).__init__(handlers, static_path="static")
        self.servers = []
        self.clients = []
        self.callback_running = 0

    def update_all_clients(self):
        if self.callback_running:
            self.callback_running += 1
            return
        for c in self.clients:
            c.gs_update_servers()
        tornado.ioloop.IOLoop.current().add_timeout(
            datetime.timedelta(seconds=2.0), self.done_waiting)
        self.callback_running = 1

    def done_waiting(self, *args):
        nb = self.callback_running
        self.callback_running = 0
        if nb > 1:
            self.update_all_clients()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("metaserver.html")


class ClientHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.gs_last_sent = None
        self.gs_prev_servers = None
        self.gs_update_servers()
        app.clients.append(self)

    def on_close(self):
        app.clients.remove(self)

    def gs_update_servers(self):
        htmltexts = [srv.gs_get_html_text(i)
                     for i, srv in enumerate(app.servers)]
        if not htmltexts:
            htmltexts = ["No connected server found"]
        text = u'\n'.join(htmltexts)
        if text != self.gs_last_sent:
            if app.servers != self.gs_prev_servers:
                text = u' ' + text
                self.gs_prev_servers = app.servers[:]
            self.write_message(text)
            self.gs_last_sent = text


class GameStatHandler(tornado.websocket.WebSocketHandler):
    gs_default_info = {'h': '?', 'p': '?', 'd': '?', 'e': 'starting',
                       'icon_dir': ICON_DIR, 'shade1': '', 'shade2': ''}

    def check_origin(self, origin):
        return True

    def open(self):
        self.gs_info = self.gs_default_info.copy()
        self.gs_info['start_time'] = time.strftime('%a %b %d<br>%H:%M GMT',
                                                   time.gmtime(time.time()))
        self.gs_info['icon'] = random.choice(ICONS)
        self.gs_info['host_ip'] = self.request.remote_ip
        app.servers.append(self)
        print 'new server on', self.gs_info['host_ip']

    def on_close(self):
        app.servers.remove(self)
        print 'removed server from', self.gs_info['host_ip']
        app.update_all_clients()

    def on_message(self, message):
        query = tornado.escape.json_decode(message)
        for key in ['h', 'p', 'd', 'e']:
            if key in query:
                value = str(query[key])[:80]
                self.gs_info[key] = tornado.escape.xhtml_escape(value)
        if self.gs_info['e'].startswith('no player'):
            self.gs_info['shade1'] = '<font color="#808080">'
            self.gs_info['shade2'] = '</font>'
        else:
            self.gs_info['shade1'] = ''
            self.gs_info['shade2'] = ''
        app.update_all_clients()

    def gs_get_html_text(self, counter):
        self.gs_info['bgcolor'] = ('#C0D0D0', '#E0D0A8')[counter & 1]
        return (
            u'<tr>'
            u'<td valign="bottom"><font size=-1>%(start_time)s</font></td>'
            u'<td valign="bottom">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
            u'<img src="%(icon_dir)s/%(icon)s">&nbsp;&nbsp;&nbsp;</td>'
            u'<td bgcolor="%(bgcolor)s"><font size=+1>'
            u'<a href="http://%(host_ip)s:%(p)s/">'
            u'<strong>%(h)s</strong>:%(p)s</a></font>'
            u'<br>%(shade1)s<strong>%(d)s</strong> (%(e)s)%(shade2)s</td>\n'
             % self.gs_info)


class FavIconHandler(tornado.web.RequestHandler):
    def get(self):
        with open('static/mfavicon.ico', 'rb') as f:
            self.write(f.read())


def main():
    global app
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
