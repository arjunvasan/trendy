import cgi
import urllib

from google.appengine.ext import ndb

import webapp2


class Passcode(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class DataTable(ndb.Model):
	created = ndb.DateTimeProperty(auto_now_add=True)
	json = ndb.JsonProperty()
	csv = ndb.TextProperty()
	url = ndb.StringProperty()