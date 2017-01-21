# Copyright 2016 Arjun Vasan <arjun.vasan@gmail.com>

from __future__ import division
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

from handlers import *
from decorators import *
from models import *

from util import pacTZ

intrinio_un = "f14a7f21a25d12f05be67615ac078841"
intrinio_pw = "2c75726a36c24361e8aeb00b769904d1"

gProps = {
    "":"Web Search",
    "news":"Google News",
    "youtube":"Youtube",
    "images":"Google Images",
    "froogle":"Google Shopping"
}

gDates = {
    "":"2004 > Today",
    "today 60-m":"Past 5 Years",
    "today 12-m":"Past Year",
    "today 90-d":"Past 90 Days",
    "today 30-d":"Past 30 Days",
    "today 7-d":"Past 7 Days"
}

def get_gDate(date_string):
    if date_string in gDates:
        return gDates[date_string]
    else:
        return date_string


class TrendyHandler(BaseHandler):
    @cache_check
    @check_trends
    def get(self):
        trend_line = self.request.get('q')

        start_date = self.request.get("date")
        stock = self.request.get("x")
        geo = self.request.get("geo")
        hide_date = False
        old = False
        frequency = 30
        hourly = False
        complete_trend = False
        start_date_normal = "2004-01-01"
        last_date = ""

        if trend_line == "":
            trend_line = urllib.unquote(self.request.get("default_q"))
        if stock == "":
            stock = urllib.unquote(self.request.get("default_x"))


        print "trend line: %s" % trend_line
        print "stock line: %s" % stock
        if not start_date:
            start_date = "today 60-m"
            
            hide_date = True

        else:
            if start_date == "today 12-m":
                frequency = 7
                complete_trend = True

            elif start_date == "today 90-d" or start_date == "today 30-d":
                complete_trend = True
                frequency = 1
            elif start_date == "today 7-d":
                frequency = 1
                hourly = True
            else:
                frequency = 7
                complete_trend = True



        if self.request.get("old"):
            old = True

        keywords = trend_line.split(",")

        ticker_time = []
        ticker_dict = {}

        if stock:

            if stock.lower() == "btc":

                if hourly:
                    request_url = "http://data.bitcoinity.org/export_data.csv?c=e&currency=USD&data_type=price&r=hour&t=l&timespan=7d"
                    result = urlfetch.fetch(request_url)
                    ticker = result.content.split("\n")[:-1]

                    ticker = [reduce(lambda x, y: x + y, map(float,filter(None,t.split(",")[1:]))) / len(filter(None,t.split(",")[1:])) for t in ticker[1:] if t]

                else:
                    date = datetime.now().strftime("%Y-%m-%d")

                    request_url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-17&end=2017-12-30"
                    result = urlfetch.fetch(request_url)
                    ticker = json.loads(result.content)

                    combined_ticker = [[k,ticker["bpi"][k]] for k in sorted(ticker["bpi"])][::frequency]

                    ticker = [ct[1] for ct in combined_ticker]
                    ticker_time = [ct[0] for ct in combined_ticker]

                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]

            elif stock.lower() == "housing":
                zipcode = self.request.get("zip")

                if not zipcode:
                    zipcode = "94041"
                request_url = "https://www.quandl.com/api/v3/datasets/ZILL/Z%s_a.json" % zipcode
                result = urlfetch.fetch(request_url)
                ticker = json.loads(result.content)["dataset"]["data"][:157]

                ticker.reverse()
                ticker = [t[1] for t in ticker]

                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]

            elif stock.lower() == "gold":
                request_url = "https://www.quandl.com/api/v3/datasets/COM/AU_LAM.json?api_key=Q6YzQTqA1mSKaaYL-Cb3&frequency=monthly"
                result = urlfetch.fetch(request_url)
                ticker = json.loads(result.content)
                ticker = [t[1] for t in ticker["dataset"]["data"]][::frequency][:157]
                ticker.reverse()
                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]

            else:
                if hourly:
                    request_url = "http://chartapi.finance.yahoo.com/instrument/1.0/%s/chartdata;type=quote;range=10d/json" % stock
                    result = urlfetch.fetch(request_url)
                    content = json.loads(result.content.replace("finance_charts_json_callback(","")[:-1])
                    ticker = []
                    current_date = ""
                    ticker_dict = {}

                    for x in content["series"]:

                        date_string = datetime.fromtimestamp(x["Timestamp"],pacTZ()).strftime("%Y-%m-%d %H")

                        if date_string != current_date:
                            #print date_string
                            current_date = date_string
                            ticker.append(x["close"])
                            ticker_dict[datetime.fromtimestamp(x["Timestamp"],pacTZ()).strftime("%Y-%m-%d %H")] = x["close"]


                    base = datetime.now(pacTZ())



                    date_list = [(base - timedelta(hours=x)).strftime("%Y-%m-%d %H") for x in range(0, 240)]
                    date_list.reverse()
                    ticker_full = []
                    started = False
                    for i,d in enumerate(date_list):
                        if d in ticker_dict:
                            if not started:
                                last_date = d
                                started = True
                            ticker_full.append(ticker_dict[d])
                            
                        else:
                            if started:
                                ticker_full.append(ticker_full[-1])

                    #ticker_full.reverse()
                    ticker = ticker_full
                    ticker_x = ticker
                    ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                    ticker = [round(100*x,4)for x in ticker]


                else:

                    if frequency == 30:
                        f = "monthly"
                    elif frequency == 7:
                        f = "weekly"
                    else:
                        f = "daily"

                    request_url = "https://api.intrinio.com/prices?identifier=%s&item=close&start_date=%s&frequency=%s" % (stock.upper(),start_date_normal,f)



                    result = urlfetch.fetch(request_url,
                                            headers={"Authorization": 
                                                     "Basic %s" % base64.b64encode("f14a7f21a25d12f05be67615ac078841:2c75726a36c24361e8aeb00b769904d1")})

                    ticker = json.loads(result.content)
                    new_ticker = []

                    ticker_dict = {}

                    if 'data' in ticker:
                        for x in ticker["data"]:
                            new_ticker.append(x["close"])
                            ticker_dict[x["date"]] = x["close"]

                        base = datetime.today()
                        if f == "daily":
                            date_list = [(base - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, 120)]
                            ticker_full = []

                            started = False
                            for i,d in enumerate(date_list):
                                if d in ticker_dict:
                                    started = True
                                    ticker_full.append(ticker_dict[d])
                                else:
                                    if started:
                                        ticker_dict[d] = ticker_full[-1]
                                        ticker_full.append(ticker_full[-1])
                            
                            ticker = ticker_full

                        else:
                            ticker = new_ticker

                        ticker.reverse()
                        ticker_x = ticker
                        ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                        ticker = [round(100*x,4)for x in ticker]
                    else:
                        ticker_x = []
                        ticker = []

        else:
            ticker = []
            ticker_x = []

        add_stocks = list(set(self.request.get("add_stocks").split(",")))
        add_trends = list(set(self.request.get("add_trends").split(",")))

        template_values = {
            'trend_line': urllib.quote(trend_line),
            'trend_clean':trend_line,
            'keywords':keywords,
            'start_date':start_date,
            'ticker_dict':ticker_dict,
            'hide_date':hide_date,
            'geo':geo,
            'stock':stock.upper(),
            'frequency':frequency,
            "hourly":hourly,
            "complete_trend":complete_trend,
            'old':old,
            'average':self.request.get("av"),
            'ticker':ticker,
            'ticker_dict':ticker_dict,
            'gprop':self.request.get("gprop"),
            'gprop_text':gProps[self.request.get("gprop")],
            'gdates_text':get_gDate(self.request.get("date")),
            'ticker_x':ticker_x,
            'url':self.request.url,
            'last_date':last_date,
            'ticker_time':ticker_time,
            'add_stocks':add_stocks,
            'add_trends':add_trends,
            'step':self.request.get("step")}

        self.render_response('index.html', **template_values)
            

app = webapp2.WSGIApplication([
    ('/.well-known/acme-challenge/([\w-]+)', LetsEncryptHandler),
    ('/cv', CVHandler),
    ('/trendy', TrendyHandler),
    ('/flush', FlushHandler),
    ('/robots.txt', BotsHandler),
    ('/r/(.*)', ReadHandler),
    ('/w/(.*)', WriteHandler),
    ('/admin/(.*)', AdminHandler),
    ('/_ah/warmup', WarmupHandler),
    ('/datatable', DataTableHandler),
    ('/.*', HomeHandler)

], debug=False)
