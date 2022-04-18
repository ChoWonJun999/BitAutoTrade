import pyupbit
import schedule
import time
import pandas as pd

"""
    볼린저 밴드 (20, 2)
"""

def get_current_price(ticker):
    """현재 가격 가져오기"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_valuation_gain_loss(ticker) :
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker :
            if b['avg_buy_price'] is not None :
                return float(b['avg_buy_price'])
            else:
                return 0

def get_balance(ticker) :
    """잔고 조회 및 가져오기"""
    balances = upbit.get_balances()

    for b in balances:
        if b['currency'] == ticker :
            if b['balance'] is not None :
                return float(b['balance'])
            else:
                return 0

def BB_1hour(ticker="KRW-BTC", cnt=20, k=2) :
    """1시간봉 볼린저 밴드"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=cnt+2)
    ma20 = pd.DataFrame(df['close'])
    ma20['mid'] = ma20['close'].rolling(window=cnt).mean()
    ma20['std'] = ma20['close'].rolling(window=cnt).std()
    ma20['upper'] = ma20['mid'] + (ma20['std'] * k)
    ma20['lower'] = ma20['mid'] - (ma20['std'] * k)
    ma20 = ma20.reset_index()
    return ma20

def BB_15minute(ticker="KRW-BTC", cnt=20, k=2) :
    """15분봉 볼린저 밴드"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=cnt+2)
    ma20 = pd.DataFrame(df['close'])
    ma20['mid'] = ma20['close'].rolling(window=cnt).mean()
    ma20['std'] = ma20['close'].rolling(window=cnt).std()
    ma20['upper'] = ma20['mid'] + (ma20['std'] * k)
    ma20['lower'] = ma20['mid'] - (ma20['std'] * k)
    ma20 = ma20.reset_index()
    return ma20

# 로그인
access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"

upbit = pyupbit.Upbit(access, secret)
print("AutoTrade Start")

ticker = "KRW-BTC"
cnt = 20
k = 2

# print(upbit.get_balances())
while True : 
    try :
        schedule.run_pending()
        current_price = get_current_price(ticker)
        krw = get_balance("KRW")
        ticker_price = get_balance(ticker[4:])
        if krw > 5000 :
            bbh = BB_1hour(ticker, cnt, k)
            if bbh.iloc[21]['close'] < bbh.iloc[21]['lower'] * 0.985 and bbh.iloc[19]['close'] < bbh.iloc[19]['lower'] :
                bbm = BB_15minute(ticker, cnt, k)
                if bbm.iloc[21]['close'] < bbm.iloc[21]['lower'] * 0.985 and bbh.iloc[19]['close'] < bbh.iloc[19]['lower'] :
                    upbit.buy_market_order(ticker, krw*0.9999)
        elif int(current_price * get_balance(ticker[4:])) > 5000 :
            if(current_price < get_valuation_gain_loss(ticker[4:])*1.015) :
                upbit.sell_market_order(ticker, ticker_price*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)