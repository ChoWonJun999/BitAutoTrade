import time
import pyupbit
import datetime
import schedule
from openpyxl import load_workbook

"""
    직전 값이 최소값일떄 매수
    직전 값이 최대값일때 매도
"""

"""API key 입력"""
access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"

def get_five_averge(ticker) :
    df = pyupbit.get_ohlcv(ticker, interval="minute10", count=7)
    df.head()
    df.tail()
    ma5 = df['close'].rolling(window=5).mean()
    ma5 = ma5.reset_index()
    return ma5

def upward_check(ma5) :
    if(int(ma5.iloc[4]['close']) > int(ma5.iloc[5]['close']) < int(ma5.iloc[6]['close']) and int(ma5.iloc[6]['close']) - int(ma5.iloc[5]['close']) >= 3000) :
        return True

def downward_check(ma5) :
    if(int(ma5.iloc[4]['close']) < int(ma5.iloc[5]['close']) > int(ma5.iloc[6]['close']) and int(ma5.iloc[5]['close']) - int(ma5.iloc[6]['close']) >= 3000) :
        return True

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
# 자동매매 시작
while True : 
    try : 
        schedule.run_pending()
        now = datetime.datetime.now()
        current_price = get_current_price(ticker)
        ma5 = get_five_averge(ticker)

        krw = get_balance("KRW")
        btc = get_balance("BTC")
        if krw > 5000 :
            """매수"""
            if upward_check(ma5) :
                load_ws.append([now, ticker, "매수", current_price, round(krw*0.9995, 0), round(krw*0.9995*0.0005, 2), round(krw*0.9995*1.0005, 0)])
                load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')
                upbit.buy_market_order(ticker, krw*0.9995)
                print(now, "\t", current_price, " 매수")
        elif btc > 0.00008 : 
            """매도"""
            if downward_check(ma5) :
                load_ws.append([now, ticker, "매도", current_price, round(btc*0.9995*current_price, 0), round(btc*0.9995*0.0005*current_price, 2), round(btc*0.9995*1.0005*current_price, 0)])
                load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')
                upbit.sell_market_order(ticker, btc*0.9995)
                print(now, "\t", current_price, " 매도")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)