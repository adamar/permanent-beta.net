#!/usr/bin/env python

import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.autoreload
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
from config import config
import torndb
import hashlib
import urlparse

from tornado.options import define, options

define("port", default=config.settings['tornado_port'], type=int)
define("mysql_host", default=config.settings['db_host'])
define("mysql_database", default= config.settings['db_database'])
define("mysql_user", default=config.settings['db_user'])
define("mysql_password", default=config.settings['db_password'])


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", mainHandler),
            (r"/new", newHandler),
            (r"/submit", submitHandler),
            (r"/vote/([^/]+)", voteHandler),
            (r"/login", loginHandler),
            (r"/logout", logoutHandler),
            (r"/signup", signupHandler),
        ]
        settings = dict(
            blog_title=u"PermanentBeta.net",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=config.settings['cookie_secret'],
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user:
            return tornado.escape.json_decode(user)
        else:
            return None

    def get_current_user_id(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return tornado.escape.json_decode(user_id)
        else:
            return None

    def get_current_message(self):
        message = self.get_secure_cookie("message") 
        if message:
            self.clear_cookie("message")
            return tornado.escape.json_decode(message)
        else:
            return ''

class mainHandler(BaseHandler):
    '''
    This Page lists all recent top links

    '''
    def get(self):
        
        query_res = self.db.query("""SELECT item_uri, item_title, 
                                       item_domain from items  
                                       order by item_votes desc limit 15""")
        self.render("index.html",
                    message=self.get_current_message(), 
                    logged_status=self.get_current_user(),
                    links=query_res)


class newHandler(BaseHandler):
    '''
    This page lists the most recently submitted links
    '''
    def get(self):
        query_res = self.db.query("""SELECT item_uri, item_title, item_domain 
                                     from items order by item_created desc 
                                     limit 15""")
        self.render("index.html",
                    message=self.get_current_message(), 
                    logged_status=self.get_current_user(),
                    links=query_res)


class submitHandler(BaseHandler):
    '''
    The link submission page for logged in users. Otherwise redirected to login page.
    '''
    def get(self):
        if not self.get_current_user():
            self.redirect("/login")
        self.render("submit.html",
                    logged_status=self.get_current_user(),
                    message=self.get_current_message())

    def post(self):
        link_title = tornado.escape.xhtml_escape(self.get_argument("link_title"))
        link_url = tornado.escape.xhtml_escape(self.get_argument("link_url"))
        link_domain = urlparse.urlparse(link_url).netloc      
        res = self.db.execute("""INSERT INTO items
                                 (item_uri, item_title, item_domain, item_user_id, item_status)
                                 VALUES ('%s', '%s', '%s','%d','active')""" % (link_url, link_title, link_domain, 1))
        #if exists in dblink_url:
        #    self.redirect("/submit?message=alreadygotthatlink")
        #else:
        #    self.db.query("insert into links (url) values ('%s')" % link_url)
        self.set_secure_cookie("message", tornado.escape.json_encode("Thanks"))
        self.redirect("/")


class voteHandler(BaseHandler):
   '''
   Vote submission
   '''
   def get(self, slug):
       if not self.get_current_user():
           self.redirect("/login")
       slug = int(''.join([i for i in slug if i in '1234567890']))
       uid = int(self.get_current_user_id())
       if self.db.query("""SELECT * from votes where item_id = %d and user_id = %d""" % (slug,uid)):
           self.redirect("/alreadyvoted")
       else:
           self.db.execute_lastrowid("""insert into votes (item_id,user_id) 
                                    VALUES (%d, %d)""" % (slug, uid))
           self.redirect("/")



class loginHandler(BaseHandler):
    '''
    Login Page
    '''
    def get(self):
        self.render("login.html",
                    logged_status=self.get_current_user(),
                    message=self.get_current_message())

    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = tornado.escape.xhtml_escape(self.get_argument("password"))
        passhash = hashlib.sha1(password+str(hashlib.sha1(password).hexdigest())).hexdigest() 
        # Hash password and use as salt to rehash
        login_res =  self.db.query("SELECT user_id, user_password FROM users WHERE user_login = '%s'" % username)
        if login_res:
            if login_res[0]['user_password'] == passhash:
                self.set_secure_cookie("user", tornado.escape.json_encode(username))
                self.set_secure_cookie("user_id", tornado.escape.json_encode(login_res[0]['user_id']))
                self.redirect("/")
        self.redirect("/bad")




class logoutHandler(BaseHandler):
    '''
    Logout Page
    '''
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")



class signupHandler(BaseHandler):
    '''
    User signup page
    '''
    def get(self):
        print "yay"
        self.render("signup.html", 
                    logged_status=self.get_current_user(),
                    message=self.get_current_message())

    def post(self):
        username = tornado.escape.xhtml_escape(self.get_argument("username"))
        password = tornado.escape.xhtml_escape(self.get_argument("password"))
        passhash = hashlib.sha1(password+str(hashlib.sha1(password).hexdigest())).hexdigest()
        email = tornado.escape.xhtml_escape(self.get_argument("email"))
        #if username == exists:
            #self.redirect("/signup" + "name_taken")
        #else:
        print "querying db"
        new = "INSERT INTO users (user_login,user_password,user_email,user_status) VALUES ('%s','%s','%s','active')" % (username, passhash, email)
        print new
        self.db.execute(new)
        print "redirecting"
        self.redirect("/")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

