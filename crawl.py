import pandas as pd
import time
import re
from urllib.request import urlopen, Request, URLError
import calendar
import datetime

def crawler():
    #read in stock code
    listofstocks = list(pd.read_csv('ds_list2010311.csv')['Stock Code'])
    ticker = []
    #format it for crawler
    for i in listofstocks:
        i = str(i)
        if len(i) < 4:
            i = '0'*(4-len(i)) + (i) + '.HK'
        else:
            i = i + '.HK'
        ticker.append(i)
    return ticker

crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
cookie_regex = r'set-cookie: (.*?); '
quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events={}&crumb={}'
##usage: download_quote(symbol, date_from, date_to, events).decode('utf-8')

def get_crumble_and_cookie(symbol):
    link = crumble_link.format(symbol)
    response = urlopen(link) #the response
    match = re.search(cookie_regex, str(response.info())) #get the cookie
    cookie_str = match.group(1)
    text = response.read().decode("utf-8")
    match = re.search(crumble_regex, text) #get the crumble
    crumble_str = match.group(1)
    return crumble_str , cookie_str #return both

def download_quote(symbol, date_from, date_to,events):
    ####### this part convert the date into format intended by Yahoo Finance
    time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
    next_day = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
    time_stamp_to = calendar.timegm(next_day.timetuple())
    ########
    attempts = 0
    while attempts < 5:
        crumble_str, cookie_str = get_crumble_and_cookie(symbol)
        link = quote_link.format(symbol, time_stamp_from, time_stamp_to, events,crumble_str)
        ##### request
        r = Request(link, headers={'Cookie': cookie_str})
        try:
            #####store the response into a csv file
            response = urlopen(r)
            text = response.read()
            with open('{}.csv'.format(symbol), 'wb') as f:
                f.write(text)
            print("{} downloaded".format(symbol))
            return b''
        except URLError:
            print ("{} failed at attempt # {}".format(symbol, attempts))
            attempts += 1
            time.sleep(2*attempts)
    return b''
    
if __name__ == '__main__':
    start_date = '2015-09-03'
    end_date = '2017-09-03'
    event = 'history'
    ticker = crawler()
    for i in ticker:
        download_quote(i,start_date,end_date,event)