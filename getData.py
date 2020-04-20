import json
import ssl
from urllib.request import urlopen
from datetime import datetime, timedelta
from urllib import parse
import requests
from bs4 import BeautifulSoup

context = ssl._create_unverified_context()
apiUrl = 'https://finance.naver.com/world/worldDayListJson.nhn?symbol=NAS@IXIC&fdtc=0&page='
telegramUrl = 'https://api.telegram.org/bot1229373667:AAEoz16l1zG6jU0uUw3cLGM7j_ws_Jq8tRo/sendMessage?chat_id=714331846&text='
telegram2Url = 'https://api.telegram.org/bot1229373667:AAEoz16l1zG6jU0uUw3cLGM7j_ws_Jq8tRo/sendMessage?chat_id=880881030&text='
nasdaqRateList = []
nasdaqMarketCapList = []
message = []
request_headers = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
Safari/537.36'), }


class NasdaqRate(object):
    def __init__(self, date, rate):
        self.date = date
        self.rate = rate


class NasdaqMarketCap(object):
    def __init__(self, name, cap):
        self.name = name
        self.cap = cap

def getNasdaqRates():
    getNasdaqRate('1')
    getNasdaqRate('2')
    getNasdaqRate('3')
    getNasdaqRate('4')
    getNasdaqRate('5')
    getNasdaqRate('6')
    # getNasdaqRate('7')
    # getNasdaqRate('8')
    if len(nasdaqRateList) > 0:
        lastDropDay = datetime.strptime(nasdaqRateList[0].date, '%Y%m%d')
        now = datetime.now()
        diff = (now - lastDropDay).days
        message.append('최근 나스닥 -3% 하락일:' + str(nasdaqRateList[0].date))
        message.append('최근 나스닥 -3% 하락일부터 오늘까지 일수:' + str(diff) + '일')
        if diff < 61:
            message.append('현재 상황:' + '공황중')
        else:
            message.append('현재 상황:' + '주식 매수')


def getNasdaqRate(page):
    nasdaqDailyData = json.loads(urlopen(apiUrl + page, context=context).read())
    if page == '1':
        message.append('최근(' + nasdaqDailyData[1]['xymd'] + ') 나스닥 등락률: ' + str(nasdaqDailyData[1]['rate']) + '%')
    for idx, dailyData in enumerate(nasdaqDailyData):
        if dailyData['rate'] <= -3:
            nasdaqRateList.append(NasdaqRate(dailyData['xymd'], dailyData['rate']))


def getNasdaqMarketCap():
    url = 'https://kr.investing.com/equities/StocksFilter?noconstruct=1&smlID=595&sid=&tabletype=fundamental&index_id=20'
    response = requests.get(url, headers=request_headers)
    soup = BeautifulSoup(response.content, "html.parser")
    nameList = soup.select('table#fundamental > tbody > tr > td:nth-child(2) > a')
    valueList = soup.select('table#fundamental > tbody > tr > td:nth-child(4)')
    nasdaqMarketCapList = listOfTuples(nameList, valueList)
    nasdaqMarketCapList.sort(key=value, reverse=True)
    message.append('Nasdaq 시총 1위 기업:' + nasdaqMarketCapList[0][0] + '(' + str(nasdaqMarketCapList[0][1]) + "B)")
    if (nasdaqMarketCapList[0][1] - nasdaqMarketCapList[1][1]) / nasdaqMarketCapList[0][1] > 0.1:
        message.append('Nasdaq 시총 2위 기업:' + nasdaqMarketCapList[1][0] + '(' + str(nasdaqMarketCapList[1][1]) + "B)")


def listOfTuples(l1, l2):
    return list(map(lambda x, y: (x.text, replaceCharToNum(y.text)), l1, l2))


def replaceCharToNum(value):
    if value.find('T') > 0:
        return float(value.replace('T', '')) * 1000
    if value.find('B') > 0:
        return float(value.replace('B', ''))


def value(t):
    return t[1]


if __name__ == '__main__':
    getNasdaqRates()
    getNasdaqMarketCap()

    print('\n'.join(message))
    urlopen(telegramUrl + parse.quote('\n'.join(message)), context=context)
    # urlopen(telegram2Url + parse.quote('\n'.join(message)), context=context)
