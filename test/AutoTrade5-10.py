import time
import pyupbit
import datetime
import schedule
from openpyxl import load_workbook

"""
    ma5 > ma10 매수
    ma5 < ma10 매도
"""

"""API key 입력"""
access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"

def get_start_time(ticker) :
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute10", count=1)

    start_time = df.index[0]
    return start_time

def chk(ticker) :
    df = pyupbit.get_ohlcv(ticker, interval="minute10", count=11)
    df.head()
    df.tail()
    ma5 = df['close'].rolling(window=5).mean()
    ma10 = df['close'].rolling(window=10).mean()
    ma5 = ma5.reset_index()
    ma10 = ma10.reset_index()
    # print(ma5.iloc[-1]['close'], ma10.iloc[-1]['close'])
    if ma5.iloc[-1]['close'] > ma10.iloc[-1]['close'] :
        return True
    else :
        return False

def get_balance(ticker) :
    """잔고 조회 및 가져오기"""
    balances = upbit.get_balances()

    for b in balances:
        if b['currency'] == ticker :
            if b['balance'] is not None :
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재 가격 가져오기"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][4]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("AutoTrade Start")

load_wb = load_workbook("C:\PythonWS\cointrade/AutoTradeLog.xlsx", data_only=True)
load_ws = load_wb['Sheet1']

ticker = "KRW-BTC"
oneTime = True
# 자동매매 시작
while True : 
    try : 
        schedule.run_pending()
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")

        # if True :
        if start_time < now < start_time + datetime.timedelta(minutes=1) and oneTime :
            krw = get_balance("KRW")
            btc = get_balance("BTC")
            current_price = get_current_price(ticker)
            # print("haha")
            if krw > 5000 :
                # print("hahaK")
                if chk(ticker) :
                    upbit.buy_market_order(ticker, krw*0.9995)
                    load_ws.append([now, ticker, "매수", current_price, round(krw*0.9995, 0), round(krw*0.9995*0.0005, 2), round(krw*0.9995*1.0005, 0)])
                    load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')
                    print(now, "\t", current_price, " 매수")
                    oneTime = False
            elif btc > 0.00008 : 
                # print("hahaB")
                if chk(ticker) == False :
                    upbit.sell_market_order(ticker, btc*0.9995)
                    load_ws.append([now, ticker, "매도", current_price, round(btc*0.9995*current_price, 0), round(btc*0.9995*0.0005*current_price, 2), round(btc*0.9995*1.0005*current_price, 0)])
                    load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')
                    print(now, "\t", current_price, " 매도")
                    oneTime = False
        else :
            oneTime = True
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)