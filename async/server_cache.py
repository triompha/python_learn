# -*- coding: utf-8 -*-

import time
import os
import datetime
import functools
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

tornado.options.parse_command_line()


IL = tornado.ioloop.IOLoop.instance()

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        '处理构建PUT和DELETE方法'

        _method = self.get_argument('_method', None)
        if _method:
            self.request.method = _method.upper()


class TestHandler(BaseHandler):
    def get(self):
        return self.write('it works!')


class LoginHandler(BaseHandler):
    '处理登陆'

    def post(self):
        return self.get()

    def get(self):
        name = self.get_argument('name', '')
        if not name:
            return self.write({'result': 1, 'msg': 'need a name'})

        if name in SessionHandler.session:
            IL.remove_timeout(SessionHandler.session[name])
        print 'set session %s ...' % name
        SessionHandler.session[name] = IL.add_timeout(time.time() + 10,
                       functools.partial(SessionHandler.remove_session, name))
        return self.write({'result': 0, 'msg': ''})


class SessionHandler(BaseHandler):
    '处理会话'

    session = {}

    @classmethod
    def remove_session(cls, name):
        print 'remove session %s ...' % name
        del cls.session[name]

    def get(self):
        return self.write({'result': 0, 'msg': '',
                           'session': self.__class__.session.keys()})



Handlers = (
    (r"/", TestHandler),
    (r"/login", LoginHandler),
    (r"/session", SessionHandler),
)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            login_url="/login",
            xsrf_cookies=False,
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            debug=False,
        )
        tornado.web.Application.__init__(self, Handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    IL.start()


if __name__ == "__main__":
    main()
