import tornado.ioloop
import tornado.web
import tornado.websocket
import bcrypt
from pymongo import MongoClient
import os, binascii
from bson.json_util import dumps
import json

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

class FoldersHandler(tornado.web.RequestHandler):
    """
    This endpoint is for dealing with a folder collection (e.g. creating a folder).

    REQUIRED HEADER: username, token
    """

    def prepare(self):
        #Allow CORS
        self.set_header("Access-Control-Allow-Origin", "*")

        #If the authentication fails, end the request. 
        if not authenticate_token(self.request.headers['username'], self.request.headers['token']):
            self.finish('ERROR: Authentication failed.')

    def post(self):
        """
        POST Request

        PURPOSE: Create a folder
        REQUIRED fields: name, dropbox_id, users
        OPTIONAL fields: pending_users, files: [{'name': string, 'in_use': boolean, 'current_user': string (or None)}]
        COMMENTS: 
            *eval(...) is used because it converts the string  self.get_argument('pending_users', '') to a Python dictionary.
            This might not be necessary when making requests from Python, not Postman. 
            *pending_users is a list of usernames to invite.
        """

        folder = {
            'name': self.get_argument('name'),
            'dropbox_id': self.get_argument('dropbox_id'),
            'files': eval(self.get_argument('files', '')),
            'users': eval(self.get_argument('users')),
            'pending_users': eval(self.get_argument('pending_users', ''))
        }
        
        db.folders.insert(folder)
        invite_users(folder)
        self.write("Folder created.")


class FoldersByIdHandler(tornado.web.RequestHandler):
    """
    This endpoint is for dealing with a specific folder only.

    REQUIRED HEADER: username, token
    """

    def prepare(self):
        #Allow CORS
        self.set_header("Access-Control-Allow-Origin", "*")

        #If the authentication fails, end the request. 
        if not authenticate_token(self.request.headers['username'], self.request.headers['token']):
            self.finish('ERROR: Authentication failed.')

    def get(self, url_dropbox_id):
        """
        GET request

        PURPOSE: Retrieve a folder object. 
        """

        #Get folders with specified id and make sure the user querying is on the folder
        folder = db.folders.find_one({ 'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']})
        self.write(dumps(folder))

    def patch(self, url_dropbox_id):
        """
        PATCH request

        PURPOSE: Update  file in folder
        OPTIONAL fields: name, in_use, current_user
        """

        #Define allowed PATCH arguments. NOTE: users and pending_users might not be necessary.
        self.allowed_patch_fields = ['name', 'users', 'pending_users']

        #Check for invalid fields
        for field in self.request.arguments.keys():
            if field not in self.allowed_patch_fields:
                self.finish("ERROR: '" + field +  "' field not allowed.")
                return

        db.folders.update( 
            {'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']},
            {'$set': {field: self.get_argument(field) for field in self.request.arguments.keys()}}
        )

        self.finish("Folder updated.")


    def put(self, url_dropbox_id):
        """
        PUT request

        PURPOSE: Add a file to the folder
        REQUIRED fields: file: {'name': string, 'in_use': boolean, 'current_user': string (or None)}
        """

        db.folders.update( 
            {'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']},
            {'$push': {'files': eval(self.get_argument('file'))}},
        )

        self.write("Folder files updated.")

    def delete(self, url_dropbox_id):
        """
        DELETE request
    
        PURPOSE: Delete a folder
        """

        db.folders.remove({'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']})
        self.finish('Folder was deleted.')

class FilesHandler(tornado.web.RequestHandler):
    """
    This endpoint is used to change files inside folders.

    REQUIRED HEADER: username, token
    """

    def prepare(self):
        #Allow CORS
        self.set_header("Access-Control-Allow-Origin", "*")

        #If the authentication fails, end the request. 
        if not authenticate_token(self.request.headers['username'], self.request.headers['token']):
            self.finish('ERROR: Authentication failed.')

    def get(self, url_dropbox_id, url_file_name):
        """
        GET request

        PURPOSE: Retrieve file object
        """
        
        folder = db.folders.find_one({'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']})
        file_index = search_in_array_of_dict(folder['files'], 'name', url_file_name)
        
        if file_index is not None:
            self.finish(dumps(folder['files'][file_index]))
            return     
        else:
            self.finish("ERROR: File '" + url_file_name + "' not found.")
            return
        

    def patch(self, url_dropbox_id, url_file_name):
        """
        PATCH request

        PURPOSE: Update  file in folder
        OPTIONAL fields: name, in_use, current_user
        """

        #Define allowed PATCH arguments
        self.allowed_patch_fields = ['name', 'in_use', 'current_user']

        #Check for invalid fields
        for field in self.request.arguments.keys():
            if field not in self.allowed_patch_fields:
                self.finish("ERROR: '" + field +  "' field not allowed.")
                return

        db.folders.update( 
            {'dropbox_id': url_dropbox_id, 'users': self.request.headers['username'], "files.name": url_file_name},
            {'$set': {'files.$.'+ field: self.get_argument(field) for field in self.request.arguments.keys()}}
        )

        self.finish("File '" + url_file_name + "' updated.")

    def delete(self, url_dropbox_id, url_file_name):
        """
        DELETE request

        PURPOSE: Delete file object
        """
        
        folder = db.folders.find_one({'dropbox_id': url_dropbox_id, 'users': self.request.headers['username']})
        file_index = search_in_array_of_dict(folder['files'], 'name', url_file_name)
        
        if file_index is not None:
            del folder['files'][file_index]
            db.folders.save(folder)

            self.finish("File '" + url_file_name + "'' was deleted.")
            return     
        else:
            self.finish("ERROR: File '" + url_file_name + "' not found.")
            return

class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
       self.render(os.path.join(PAGES_PATH, 'register.html'))
   
    def post(self):
        username = self.get_argument('username')
        password = bcrypt.hashpw(self.get_argument('password').encode("utf-8"), bcrypt.gensalt())
        
        if not db.users.find({'username': username}).count():
            db.users.insert({
                'username': username, 
                'password': password, 
                'tokens': [], 
                'folders': [],
                'invites': []
            })
        
        else:
            self.write('User already exists.')

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
        (r"/api/folders/?", FoldersHandler)
    ], cookie_secret = 'CSOxb5p1sUcu24bW6pee',**settings)

    application.listen(port)
    print "Listening on port: %s" % (port)

    tornado.ioloop.IOLoop.instance().start()