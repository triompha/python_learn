# -*- coding: utf-8 -*-

import re
import functools
import datetime
import random
import tornado.httpserver
import tornado.web
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient

IL = tornado.ioloop.IOLoop.instance()
RSS_URL = 'http://www.sooip.cn/e/web/?type=rss2&classid=1'
LINK_URL = re.compile('<link>([^<]*?)</link>')
IP_RE = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} \d{2,5}) HTTP')
IP = []
ALL_URL = []


def fetch_rss(url, callback):
    print 'to fetch rss %s ...' % url
    AsyncHTTPClient().fetch(url, callback=callback)

def on_rss_fetch(response):
    global ALL_URL
    ALL_URL = LINK_URL.findall(response.body)
    print 'get %d url' % len(ALL_URL)
    IL.add_callback(functools.partial(fetch_page,
                                      ALL_URL.pop(), on_page_fetch))


def fetch_page(url, callback):
    print 'to fetch page %s ...' % url
    AsyncHTTPClient().fetch(url, callback=callback)

def on_page_fetch(response):
    global ALL_URL
    global IP
    ip_list = IP_RE.findall(response.body)
    print 'get %d ip' % len(ip_list)
    IP.extend(ip_list)
    if ALL_URL:
        print 'continue ...'
        IL.add_timeout(datetime.timedelta(seconds=5),
                       functools.partial(fetch_page,
                                         ALL_URL.pop(), on_page_fetch))
    else:
        global checker
        checker.start()

def check_new():
    '检查是否有更新'
    global checker
    if True:
        print 'check ok'
        checker.stop()
        fetch_rss(RSS_URL, on_rss_fetch)
    else:
        print 'check fail'


class IpHandler(tornado.web.RequestHandler):
    def get(self):
        global IP
        try:
            return self.write(random.choice(IP))
        except IndexError:
            return self.write('no ip')

Handlers = (
    ('/ip', IpHandler),
)
app = tornado.web.Application(Handlers)
checker = tornado.ioloop.PeriodicCallback(check_new, 5000)
def main():
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(8888)
    #fetch_rss(RSS_URL, on_rss_fetch)
    checker.start()
    IL.start()

if __name__ == '__main__':
    main()
