import pandas as pd
import time
import re, os
from urllib.request import urlopen, Request, URLError
import calendar
import datetime


def crawler(fulllist=False):
    a['shortsellable','fulllist']
    print(a[fulllist])
    #read in stock code
    listofstocks = list(pd.read_csv('ds_list20190311.csv',index_col=False)['Stock Code'])
    ticker = []
    #format it for crawler
    for i in listofstocks:
        i = str(i)
        if len(i) < 4:
            i = '0'*(4-len(i)) + (i) + '.HK'
        else:
            i = i + '.HK'
        ticker.append(i)
    if fulllist:
        df = pd.read_csv('Fulllist.csv',usecols=['Stock Code','Category'],dtype='str').dropna()
        full = list(df.loc[df['Category'] == 'Equity']['Stock Code'])
        ticker = [i[1:]+'.HK' for i in full]
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
            with open(os.path.join('stock_data/{}.csv'.format(symbol)), 'wb') as f:
                f.write(text)
            print("{} downloaded".format(symbol))
            return b''
        except URLError:
            print ("{} failed at attempt # {}".format(symbol, attempts))
            attempts += 1
            time.sleep(2)
    return b''
    
if __name__ == '__main__':
    now = datetime.datetime.now()
    end_date = now.strftime ("%Y-%m-%d")
    start_date = (now - datetime.timedelta(days=90)).strftime ("%Y-%m-%d")
    event = 'history'
    ticker = crawler(fulllist=True)
    for i in ticker:
        download_quote(i,start_date,end_date,event)