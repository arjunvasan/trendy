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

class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)