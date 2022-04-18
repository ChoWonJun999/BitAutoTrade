import time
import pyupbit
import datetime
import schedule
import numpy as np
from openpyxl import load_workbook

"""
    변동성 전략
"""

access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"

def get_target_price(ticker, k) :
    """매수 가격 설정"""
    df = pyupbit.get_ohlcv(ticker, interval='minute60', count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker) :
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1)
    start_time = df.index[0]
    return start_time

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
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ror(k=0.5, ticker="KRW-BTC") :
    df = pyupbit.get_ohlcv(ticker, interval='minute60')
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.9995
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] * fee, 1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_bestK(ticker="KRW-BTC") :
    """Best K 값 구하기"""
    bestK = 0.0
    bestror = 0.0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k, ticker)
        if bestror < ror :
            bestror = ror
            bestK = k
    return bestK

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("AutoTrade Start")

load_wb = load_workbook("C:\PythonWS\cointrade/AutoTradeLog.xlsx", data_only=True)
load_ws = load_wb['Sheet1']

ticker = pyupbit.get_high_volume_ticker()
bestK = get_bestK(ticker)

print("---------------시작---------------")
print("ticker = ", ticker)
print("now = ", datetime.datetime.now())
print("bestK = ", bestK)

reset = True
# 자동매매 시작
while True : 
    try : 
        now = datetime.datetime.now()
        start_time = get_start_time(ticker)
        end_time = start_time + datetime.timedelta(hours=1)

        if(reset) :
            chk_ticker = pyupbit.get_high_volume_ticker()
            chk_bestK = get_bestK(chk_ticker)
            if(ticker != chk_ticker or bestK != chk_bestK) : 
                ticker = chk_ticker
                bestK = chk_bestK
                print("---------------리셋---------------")
                print("ticker = ", ticker)
                print("now = ", now)
                print("bestK = ", bestK)
        
        schedule.run_pending()
        current_price = get_current_price(ticker)
        # 매매 시작~종료 시간에 매수
        if start_time < now < (end_time - datetime.timedelta(seconds=10)) :
            target_price = get_target_price(ticker, bestK)
            if target_price < current_price :
                krw = get_balance("KRW")
                if krw > 5000 :
                    upbit.buy_market_order(ticker, krw*0.9995)
                    load_ws.append([now, ticker, "매수", current_price, round(krw*0.9995, 0), round(krw*0.9995*0.0005, 2), round(krw*0.9995*1.0005, 0)])
                    load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')

                    reset = False
                    print("---------------매수---------------")
                    print("ticker = ", ticker)
                    print("now = ", now)
                    print("current_price = ", current_price)
        # 이외 매도
        else:
            ticker_price = get_balance(ticker[4:])
            if int(current_price * get_balance(ticker[4:])) > 5000 :
                upbit.sell_market_order(ticker, ticker_price*0.9995)
                load_ws.append([now, ticker, "매도", current_price, round(ticker_price*0.9995*current_price, 0), round(ticker_price*0.9995*0.0005*current_price, 2), round(ticker_price*0.9995*1.0005*current_price, 0)])
                load_wb.save('C:\PythonWS\cointrade/AutoTradeLog.xlsx')

                reset = True
                print("---------------매도---------------")
                print("ticker = ", ticker)
                print("now = ", now)
                print("current_price = ", current_price)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)