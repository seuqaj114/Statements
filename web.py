import tornado.ioloop
import tornado.web
import tornado.websocket
import bcrypt
from pymongo import MongoClient
import os, binascii
from bson.json_util import dumps
import json

import analyse

#client = MongoClient("mongodb://dibbs:dibbs@kahana.mongohq.com:10033/dibbs_db")
#db = client.dibbs_db

dirname = os.path.dirname(__file__)
TEMPLATES_PATH = os.path.join(dirname, 'templates')

settings = { 
    'static_path': os.path.join(dirname, 'static')
    }

port = 8000


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

class LoginHandler(tornado.web.RequestHandler):
    def prepare(self):
        #Allow CORS
        self.set_header("Access-Control-Allow-Origin", "*")
    
    def get(self):
        self.render(os.path.join(PAGES_PATH, 'login.html'))
   
    def post(self):
        user = db.users.find_one({'username': self.get_argument('username')})
        
        if bcrypt.hashpw(self.get_argument('password').encode("utf-8"), user['password'].encode("utf-8")) == user['password']:
            #Generate a token and hash it
            token = binascii.hexlify(os.urandom(20))
            #Append the token to the user token list
            user['tokens'].append(bcrypt.hashpw(token, bcrypt.gensalt()))
            db.users.save(user)
            self.write(json.dumps({"valid":True, "token":token}))
        else:
            self.write(json.dumps({"valid":False, "error":"Authentication failed."}))

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/analyse?", AnalyseHandler)
    ], cookie_secret = 'CSOxb5p1sUcu24bW6pee',**settings)

    application.listen(port)
    print "Listening on port: %s" % (port)

    tornado.ioloop.IOLoop.instance().start()