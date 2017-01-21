from webapp2_extras import jinja2
import webapp2
import os
import json
import base64
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from datetime import datetime, timedelta
from itertools import islice, tee

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb

from decorators import *
from models import *


class BaseHandler(webapp2.RequestHandler):

    found_in_cache = False
    cached_url = None
    cached_data = None

    def __init__(self, request, response):
        self.initialize(request, response)
    	url = self.request.url
        qs = urllib.unquote(self.request.query_string)
    	rv = memcache.get(url)

    	if rv:
            self.found_in_cache = True
            self.cached_url = rv
            if qs:
                self.cached_data = memcache.get("data:%s" % qs)
                #if not self.cached_data:
                    #self.cached_data = DataTable.get_by_id(qs).to_dict()

                if self.cached_data:
                    self.cached_url = self.cached_url + "<script type='text/javascript'>cached_data = %s;</script>" % json.dumps(self.cached_data["json"])


    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        if self.request.get("flush"):
        	memcache.flush_all()
        	#print "memcache flushed"

        url = self.request.url

        context["path"] = self.request.path
        context["qs"] = urllib.unquote(self.request.query_string)

        if context["path"] == '/trendy':
            context["page_title"] = "Trendy = Google Trends + ??"
        else:
            context["page_title"] = "Arjun Lives Here .. "

    	rv = self.jinja2.render_template(_template, **context)
    	if not memcache.set(url,rv,86400):
    		print "memcache didn't work"
    	else:
    		pass

    	

       	self.response.write(rv)




class DataTableHandler(webapp2.RequestHandler):
    def get(self):
        pass
    def post(self):

        dt = DataTable(
            id = urllib.unquote(self.request.get("url")),
            json = json.loads(self.request.get("json")),
            csv = self.request.get("csv"),
            url = urllib.unquote(self.request.get("url")))
        cached = memcache.set("data:%s" % dt.url,dt.to_dict(),86400)
        self.response.out.write(dt.put())

class FlushHandler(BaseHandler):
    def get(self):
        memcache.flush_all()
        self.redirect("/")

class IndexHandler(BaseHandler):
    def get(self):
        template_values = {
            "q":"ARJUNV",
            "page":"trendy.html"
        }
        self.render_response('index.html', **template_values)

class HomeHandler(BaseHandler):
    def get(self):
        template_values = {
            "q":"ARJUNV",
            "page":"home.html"
        }
        self.render_response('index.html', **template_values)

class CVHandler(BaseHandler):
    @pass_code
    def get(self):
        template_values = {
            "q":"ARJUNV",
            "page":"cv_template.html"
        }
        self.render_response('index.html', **template_values)


class BotsHandler(BaseHandler):
    def get(self):
        template_values = {
            "q":"ARJUNV",
            "page":"robots.txt"
        }
        self.response.headers['Content-Type'] = 'text/plain'
        self.render_response('robots.txt', **template_values)

class WriteHandler(BaseHandler):
    def get(self,article):
        template_values = {
            "q":"ARJUNV",
            "page":"write.html",
            "article":article,
            "editor":True
        }

        self.render_response('index.html', **template_values)

class ReadHandler(BaseHandler):
    def get(self,article):
        template_values = {
            "q":"ARJUNV",
            "page":"article.html",
            "article":article
        }

        self.render_response('index.html', **template_values)



class AdminHandler(BaseHandler):
    def post(self,page):
        if self.request.get("key") != "":
            code = Passcode(id=self.request.get("key"),email=self.request.get("email"))
        else:
            code = Passcode(email=self.request.get("email"))

        key = code.put()
        self.response.out.write(key)

    def get(self,page):
        codes = Passcode.query().order(Passcode.created)
        template_values = {
            "q":"ARJUNV",
            "page":"admin.html",
            "codes":codes
        }

        self.render_response('index.html', **template_values)


class LetsEncryptHandler(BaseHandler):
    def get(self, challenge):
        self.response.headers['Content-Type'] = 'text/plain'
        responses = {
            'G3jhPABr9APlTcyU3BiICwtqs_AVaR1AzKppJjO8Z58': 'G3jhPABr9APlTcyU3BiICwtqs_AVaR1AzKppJjO8Z58.vt94TdBucSAWgNHK4VUWz_Nf00lkPSNwKAQpi_0KkQk',
            'YALKBsgBIvbj7iEoNYWY_CzKMN2U0KZWn1I2yEeoUgY': 'YALKBsgBIvbj7iEoNYWY_CzKMN2U0KZWn1I2yEeoUgY.vt94TdBucSAWgNHK4VUWz_Nf00lkPSNwKAQpi_0KkQk',
            "rURcx2oM1U4wuW-r9ZDBLbf2BMUUC157TwRkRcpK7tA":"rURcx2oM1U4wuW-r9ZDBLbf2BMUUC157TwRkRcpK7tA.7e4u3VNKr-rZiCl2RsTSVvfH19bv0G5NUMpiHY-Avvc",
            "Hq8tZ5ugqGoJe6mQehJfWemhh3TZ0N8tAaOb_mKZf-8":"Hq8tZ5ugqGoJe6mQehJfWemhh3TZ0N8tAaOb_mKZf-8.fs4oqnfjcrF9jxTSKCYeoO1TNBXfZiXiJk3yJ3gXpQ8"}
        if challenge in responses:
            self.response.out.write(responses[challenge])
        else:
            self.response.out.write("no response")


class WarmupHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Warmup successful')
