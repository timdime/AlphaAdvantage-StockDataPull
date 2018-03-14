# Stock Trading Strategy Data Collector
# tdime 7/29

import os.path
import urllib2
from datetime import date, timedelta
from bs4 import BeautifulSoup
try:
    from urllib.request import Request, urlopen
except ImportError:  # python 2
    from urllib2 import Request, urlopen

TIME_INTERVAL = ['1min','Daily'] #['5min','1min','Daily'] # ['1min', '5min', '15min', '30min', '60min', 'Daily', 'Weekly']

TICKERLISTSITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
HISTORICAL_DATA_PATH = "./HistoricalData/"
APIKEY = 'your free API key from www.alphavantage.co'

INTRADAYURL = ('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={0}&outputsize=full&interval={1}&apikey=%s&datatype=csv' % APIKEY)
URL = ('https://www.alphavantage.co/query?function=TIME_SERIES_{1}&symbol={0}&outputsize=compact&apikey=%s&datatype=csv' % APIKEY)

DAYS_BACK_OF_INTEREST = 9

RECENT_WEEKDAYS = []

while DAYS_BACK_OF_INTEREST > 0:
    day_of_week = date.weekday(date.today() - timedelta(DAYS_BACK_OF_INTEREST))
    if day_of_week < 5:
        RECENT_WEEKDAYS.append((date.today() - timedelta(DAYS_BACK_OF_INTEREST)).strftime("%Y-%m-%d"))
    DAYS_BACK_OF_INTEREST -= 1


def scrape_list(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page, "lxml")

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip())
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers


def validFileExists(fname):
    if os.path.isfile(fname):
        if os.path.getsize(fname)>2:
            return True
        else:
            return False
    else:
        return False

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_snp500():
    sector_tickers = scrape_list(TICKERLISTSITE)
    for sector in sector_tickers:
        for ticker in sector_tickers[sector]:
#            if ticker=="ALK":
                for interval in TIME_INTERVAL:
                    data = GetData(ticker, interval)
                    for date in RECENT_WEEKDAYS:
                        filepath = "%s%s/%s/%s_%s_%s.csv" % (HISTORICAL_DATA_PATH, sector, ticker, date, ticker, interval)
                        if validFileExists(filepath) == False:
                            ensure_dir(filepath)
                            print "logging Sector: %s -- Symbol: %s -- Interval: %s -- Date: %s" % (sector, ticker, interval, date)
                            saveData(data, ticker, interval, date, filepath)
                        else:
                            print "* skipping Sector: %s -- Symbol: %s -- Interval: %s" % (sector, ticker, interval)

def saveData(data, tickers, interval, date, filepath):
    data = data.split("\n")
    headers = "%s\n" % data[0]
    csv_file = open(filepath, "w")
    csv_file.write(headers)
    for line in data:
        if line.split(",")[0].split(" ")[0] == date:
            csv_file.write("%s\n" % line)
    csv_file.close()


def GetData(symbol, interval):

    if "min" in interval: 
        url = str.format(INTRADAYURL, symbol, interval)
    else:
        url = str.format(URL, symbol, interval)
    print url
    req = Request(url)
    try:
        resp = urlopen(req)
    except:
        time.sleep(5)
        resp = urlopen(req)
    content = resp.read().decode('ascii', 'ignore').strip()
    return content

if __name__ == '__main__':
    get_snp500()



       
