# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import division

import webapp2

import os
import json
import base64
import urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

from datetime import datetime, timedelta


intrinio_un = "f14a7f21a25d12f05be67615ac078841"
intrinio_pw = "2c75726a36c24361e8aeb00b769904d1"



from itertools import islice, tee

def moving_average(n, iterable):
    # leading 0s
    for i in range(1, n):
        yield 0.

    # actual averages
    head, tail = tee(iterable)
    sum_ = float(sum(islice(head, n)))
    while True:
        yield sum_ / n
        sum_ += next(head) - next(tail)


class BtcData(webapp2.RequestHandler):
    def get(self):
        request_url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-22&end=2017-12-30"
        result = urlfetch.fetch(request_url)

        result = urlfetch.fetch(request_url)
        ticker = json.loads(result.content)

        csv = ["%s,%s" % (k,ticker["bpi"][k]) for k in sorted(ticker["bpi"])][::7]

        csv_text = "<br>".join(csv)

        ticker = [ticker["bpi"][k] for k in sorted(ticker["bpi"])][::7]



        self.response.out.write(csv_text)


class AddTrend(webapp2.RequestHandler):
    def get(self):
        q = self.request.get("q")
        date = self.request.get("date")
        geo = self.request.get("geo")
        prop = self.request.get("prop")
        request_url = 'https://www.google.com/trends/fetchComponent?q=%s&cid=TIMESERIES_GRAPH_0&export=3&date=%s&geo=%s&gprop=%s' % (q,date,geo,prop)

        result = urlfetch.fetch(request_url)

        self.response.out.write(result.content)




class AddStock(webapp2.RequestHandler):
    def get(self):

        if stock:

            if stock.lower() == "btc":
                request_url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-17&end=2017-12-30"
                result = urlfetch.fetch(request_url)
                ticker = json.loads(result.content)
                ticker = [ticker["bpi"][k] for k in sorted(ticker["bpi"])][::30]


                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]

            elif stock.lower() == "housing":
                zipcode = self.request.get("zip")
                if not zipcode:
                    zipcode = "94041"
                request_url = "https://www.quandl.com/api/v3/datasets/ZILL/Z%s_a.json" % zipcode
                result = urlfetch.fetch(request_url)
                ticker = result.content["data"][:157]

                ticker = [ticker["data"][k] for k in sorted(ticker["data"])]

                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]


                #print ticker

            elif stock.lower() == "gold":
                request_url = "https://www.quandl.com/api/v3/datasets/COM/AU_LAM.json?api_key=Q6YzQTqA1mSKaaYL-Cb3&frequency=monthly"
                result = urlfetch.fetch(request_url)
                ticker = json.loads(result.content)
                print ticker["dataset"]["data"]




            else:
                request_url = "https://api.intrinio.com/prices?identifier=%s&item=close&start_date=2004-01-01&frequency=monthly" % stock.upper()

                print request_url

                result = urlfetch.fetch(request_url,
                                        headers={"Authorization": 
                                                 "Basic %s" % base64.b64encode("f14a7f21a25d12f05be67615ac078841:2c75726a36c24361e8aeb00b769904d1")})

                ticker = json.loads(result.content)

                ticker = [x["close"] for x in ticker["data"]]

                ticker.reverse()

                ticker_x = ticker

                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]

                ticker = [round(100*x,4)for x in ticker]
        else:
            ticker = []
            ticker_x = []


def getTicker(symbol):
    if symbol:

        if symbol.lower() == "btc":
            request_url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-17&end=2017-12-30"
            result = urlfetch.fetch(request_url)
            ticker = json.loads(result.content)
            ticker = [ticker["bpi"][k] for k in sorted(ticker["bpi"])][::30]


            ticker_x = ticker
            ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
            ticker = [round(100*x,4)for x in ticker]

        elif symbol.lower() == "housing":
            zipcode = self.request.get("zip")
            print zipcode
            if not zipcode:
                zipcode = "94041"
            request_url = "https://www.quandl.com/api/v3/datasets/ZILL/Z%s_a.json" % zipcode
            result = urlfetch.fetch(request_url)
            ticker = json.loads(result.content)["dataset"]["data"][:157]

            ticker.reverse()

            ticker = [t[1] for t in ticker]

            print ticker

            ticker_x = ticker
            ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
            ticker = [round(100*x,4)for x in ticker]

        elif symbol.lower() == "gold":
            request_url = "https://www.quandl.com/api/v3/datasets/COM/AU_LAM.json?api_key=Q6YzQTqA1mSKaaYL-Cb3&frequency=monthly"
            result = urlfetch.fetch(request_url)
            ticker = json.loads(result.content)
            ticker = [t[1] for t in ticker["dataset"]["data"]][::30][:157]
            ticker.reverse()
            ticker_x = ticker
            ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
            ticker = [round(100*x,4)for x in ticker]


        else:
            request_url = "https://api.intrinio.com/prices?identifier=%s&item=close&start_date=2004-01-01&frequency=monthly" % stock.upper()

            print request_url

            result = urlfetch.fetch(request_url,
                                    headers={"Authorization": 
                                             "Basic %s" % base64.b64encode("f14a7f21a25d12f05be67615ac078841:2c75726a36c24361e8aeb00b769904d1")})

            ticker = json.loads(result.content)
            ticker = [x["close"] for x in ticker["data"]]
            ticker.reverse()
            ticker_x = ticker
            ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
            ticker = [round(100*x,4)for x in ticker]
    else:
        ticker = []
        ticker_x = []

    return ticker,ticker_x


class MainPage(webapp2.RequestHandler):
    def get(self):

        trend_line = self.request.get('trend_line')
        print "trend_line: %s" % trend_line
        start_date = self.request.get("date")
        stock = self.request.get("stock")
        geo = self.request.get("geo")
        hide_date = False
        old = False
        frequency = 30
        hourly = False
        complete_trend = False
        start_date_normal = "2004-01-01"
        if not start_date:
            start_date = "today 5-y"
            
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

        if not trend_line:
            trend_line = "trump"

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
                    print ticker[:-1]
                    ticker = [reduce(lambda x, y: x + y, map(float,filter(None,t.split(",")[1:]))) / len(filter(None,t.split(",")[1:])) for t in ticker[1:] if t]

                else:
                    date = datetime.now().strftime("%Y-%m-%d")

                    request_url = "https://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-17&end=2017-12-30"
                    result = urlfetch.fetch(request_url)
                    ticker = json.loads(result.content)
                    #ticker_time = [k for k in sorted(ticker["bpi"])][::frequency]
                    #ticker_time = json.dumps(ticker_time);
                    #print sorted(ticker["bpi"])
                    #print "hello"


                    #ticker_time = ticker_time.replace("&quot;",'"')
                    combined_ticker = [[k,ticker["bpi"][k]] for k in sorted(ticker["bpi"])][::frequency]

                    ticker = [ct[1] for ct in combined_ticker]
                    ticker_time = [ct[0] for ct in combined_ticker]
                    print "hellotime"
                    print ticker_time
                    
                    

                    #ticker = list(moving_average(3,ticker))


                ticker_x = ticker
                ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                ticker = [round(100*x,4)for x in ticker]

            elif stock.lower() == "housing":
                zipcode = self.request.get("zip")
                print zipcode
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
                    print "hourly"
                    for x in content["series"]:
                        date_string = datetime.fromtimestamp(x["Timestamp"]).strftime("%Y-%m-%d %H")

                        if date_string != current_date:
                            current_date = date_string
                            ticker.append(x["close"])
                            ticker_dict[datetime.fromtimestamp(x["Timestamp"]).strftime("%Y-%m-%d %H")] = x["close"]


                    #print ticker_dict

                    base = datetime.today()
                    date_list = [(base - timedelta(hours=x)).strftime("%Y-%m-%d %H") for x in range(0, 240)]
                    
                    ticker_full = []
                    started = False
                    for i,d in enumerate(date_list):
                        if d in ticker_dict:
                            started = True
                            ticker_full.append(ticker_dict[d])
                        else:
                            if started:
                                ticker_full.append(ticker_full[-1])

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

                    print request_url

                    result = urlfetch.fetch(request_url,
                                            headers={"Authorization": 
                                                     "Basic %s" % base64.b64encode("f14a7f21a25d12f05be67615ac078841:2c75726a36c24361e8aeb00b769904d1")})

                    ticker = json.loads(result.content)

                    new_ticker = []


                    ticker_dict = {}
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
                                print d, ticker_dict[d]
                            else:
                                if started:
                                    ticker_dict[d] = ticker_full[-1]
                                    print d, ticker_full[-1]
                                    ticker_full.append(ticker_full[-1])
                        

                        ticker = ticker_full
                        #print ticker_full,len(ticker_full)
                    else:
                        ticker = new_ticker


                    
                    ticker.reverse()
                    #ticker_date.reverse()



                    #d = [datetime.strptime(d,"%Y-%m-%d") for d in ticker_date]

                    #date_set = set(d[0] + timedelta(x) for x in range((d[-1] - d[0]).days))
                    #missing = sorted(date_set - set(d))


                    #print ticker_date

                    ticker_x = ticker
                    ticker = [(x-min(ticker))/(max(ticker)-min(ticker)) for x in ticker]
                    ticker = [round(100*x,4)for x in ticker]


        else:
            ticker = []
            ticker_x = []

        
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
            'ticker_x':ticker_x,
            'url':self.request.url,
            'ticker_time':ticker_time,
            'step':self.request.get("step")}


        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/btc', BtcData),
    ('/addTrend', AddTrend)
], debug=True)
