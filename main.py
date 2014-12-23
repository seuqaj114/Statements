import tornado.ioloop
import tornado.web
import tornado.httpserver

from pymongo import MongoClient
import os, binascii
from bson.json_util import dumps
import json

import analyse

#client = MongoClient("mongodb://dibbs:dibbs@kahana.mongohq.com:10033/dibbs_db")
#db = client.dibbs_db

dirname = os.path.dirname(__file__)
TEMPLATES_PATH = os.path.join(dirname, 'templates')
FAVICON_PATH = os.path.join(dirname,"favicon.ico")

settings = { 
    'static_path': os.path.join(dirname, 'static')
    }


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join(TEMPLATES_PATH, 'main.html'))

class AnalyseHandler(tornado.web.RequestHandler):

    def prepare(self):
        #Allow CORS
        self.set_header("Access-Control-Allow-Origin", "*")

    def post(self):
        raw_text = self.get_argument("text",None)
        print raw_text

        stars,probs = analyse.calculate_document_probabilities(raw_text)

        print stars, probs
        self.finish({"stars":stars,"probs":probs})

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/analyse?", AnalyseHandler),
        (r'/favicon.ico', tornado.web.StaticFileHandler, {'path': favicon_path})
    ], cookie_secret = 'CSOxb5p1sUcu24bW6pee',**settings)

    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)

    #application.listen(port)
    
    print "Listening on port: %s" % (port)

    tornado.ioloop.IOLoop.instance().start()