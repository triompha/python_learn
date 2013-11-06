# -*- coding: utf-8 -*-

import time
import os
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


GlobalVar = ''
class GlobalVarHandler(BaseHandler):
    '全局变量'

    def get(self):
        global GlobalVar
        return self.write(u'现在 v 的值是: ' + GlobalVar)
    
    def post(self):
        global GlobalVar
        v = self.get_argument('v', '')
        GlobalVar += v
        return self.write('0')

    def delete(self):
        global GlobalVar
        GlobalVar = ''
        return self.write('0')


class ViolenceHandler(BaseHandler):
    '暴力请求'

    count = {}
    last = 0

    def get(self):
        ip = self.get_argument('ip', '')
        if not ip:
            return self.write({'result': 1, 'msg': 'need a ip'})

        cls = self.__class__
        now = int(time.time())
        if now - cls.last > 60:
            cls.count = {}
            cls.last = now

        if ip in cls.count:
            if cls.count[ip] > 10:
                return self.write({'result': 2, 'msg': ''})
            else:
                cls.count[ip] += 1
        else:
            cls.count[ip] = 1

        return self.write({'result': 0, 'msg': cls.count[ip]})


    def post(self):
        ip = self.get_argument('ip', '')
        if not ip:
            return self.write({'result': 1, 'msg': 'need a ip'})

        self.__class__.count[ip] = 9999
        return self.write({'result': 0, 'msg': ''})



Handlers = (
    (r"/", TestHandler),
    (r"/global-var", GlobalVarHandler),
    (r"/violence", ViolenceHandler),
)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            login_url="/login",
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )
        tornado.web.Application.__init__(self, Handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    IL.start()


if __name__ == "__main__":
    main()
