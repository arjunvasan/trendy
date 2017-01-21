from functools import wraps
import cgi
import urllib

from google.appengine.ext import ndb

from models import *

import webapp2


# for private info
def pass_code(handler):
    @wraps(handler)
    def wrapper(self, *args, **kwargs):
        if self.request.url.find("trendy-154222") > -1:
            self.redirect("https://arjunvasan.com/trendy?%s" % self.request.query_string)
        else:
            key = self.request.get("key")
            template_values = {"page":"locked.html"}

            if key:
                code = Passcode.get_by_id(self.request.get("key"))
                if code and code.email == self.request.get("email"):
                    return handler(self, *args, **kwargs)
                else:
                    self.render_response("index.html", **template_values)

            else:
                self.render_response("index.html", **template_values)
    return wrapper

def is_domain(handler):
    @wraps(handler)
    def wrapper(self, *args, **kwargs):
        if self.request.url.find("trendy-154222") > -1:
            self.redirect("https://arjunvasan.com/trendy?%s" % self.request.query_string)
        else:
            pass
    return wrapper


# if no trend specified, render Trendy home page
def check_trends(handler):
    @wraps(handler)
    def wrapper(self, *args, **kwargs):
        if not self.request.get("q") and not self.request.get("default_q"):
            template_values = {
                "q":"ARJUNV",
                "page":"trendy.html"
            }
            self.render_response('index.html', **template_values)
        else:
            return handler(self, *args, **kwargs)
    return wrapper

# simple decorator to wrap handler's with a quick memcache check
def cache_check(handler):
    @wraps(handler)
    def wrapper(self, *args, **kwargs):
        if self.found_in_cache:
            self.response.out.write(self.cached_url)
        else:
            return handler(self, *args, **kwargs)
    return wrapper

if __name__ == "__main__":
    cache_check()
    pass_code()

