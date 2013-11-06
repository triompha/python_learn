# -*- coding: utf-8 -*-

import time
import os
import datetime
import functools
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import sqlite3

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

tornado.options.parse_command_line()


IL = tornado.ioloop.IOLoop.instance()

#'创建数据库'
conn = sqlite3.connect(':memory:')
CONN = conn
c = conn.cursor()
c.execute('''
CREATE TABLE Main (id integer PRIMARY KEY, name varchar(32));
''')
conn.commit()
c.close()

c = conn.cursor()
for i in range(10):
    sql = 'insert into Main (name) values (%s)' % (i + 10)
    c.execute(sql)
conn.commit()
c.close()

#c = conn.cursor()
#c.execute('select id, name from Main where id in (1,2,3,4)')
#print c.fetchall()
#c.close()


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        '处理构建PUT和DELETE方法'

        _method = self.get_argument('_method', None)
        if _method:
            self.request.method = _method.upper()


class TestHandler(BaseHandler):
    def get(self):
        return self.write('it works!')


class ProxyHandler(BaseHandler):
    request = {}

    @tornado.web.asynchronous
    def get(self):
        id = self.get_argument('id', '')
        id = int(id)
        cls = self.__class__
        if not id:
            return self.finish({'result': 1, 'msg': 'need a id'})
        else:
            if id in cls.request:
                cls.request[id].append(self)
            else:
                cls.request[id] = [self]


class SQLTimer(tornado.ioloop.PeriodicCallback):
    '定时查库返回结果'

    def __init__(self, callback_time):
        super(SQLTimer, self).__init__(self.sql, callback_time)

    def sql(self):
        request = ProxyHandler.request.copy()
        ProxyHandler.request = {}
        ids = request.keys()
        print 'ids: %s' % str(ids)
        sql = 'select id, name from Main where id in (%s)' % (', '.join(['?'] * len(ids)))
        print 'sql: %s' % sql
        c = CONN.cursor()
        c.execute(sql, ids)
        r = c.fetchall()
        c.close()

        for id, name in r:
            for req in request[id]:
                req.finish({'result': 0, 'name': name})



Handlers = (
    (r"/", TestHandler),
    (r"/proxy", ProxyHandler),
)


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            login_url="/login",
            xsrf_cookies=False,
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )
        tornado.web.Application.__init__(self, Handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    SQLTimer(2000).start()
    IL.start()


if __name__ == "__main__":
    main()
