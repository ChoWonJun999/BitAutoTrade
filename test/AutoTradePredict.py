import time
import pyupbit
import datetime
import requests
import schedule
from fbprophet import Prophet
import numpy as np

"""
    조코딩 참고
    예측값 포함
"""

# API key 입력
access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"
# myToken = "xoxb-your-token"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k) :
    """매수 가격 설정"""
    # 가격 데이터
    # interval = month/week/day/minute1, minute3, minute5, minute10, minute15, minute30, minute60, minute240
    # count = integer(default=200)
    # 1일 기준 2개의 테이터
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    # print("df", df)

    # 매수 가격 계산
    # 래리 윌리엄스(Larry R. Williams)의 변동성 돌파 전략
    # 변동성 돌파 전략에 따른 매수가 = 전일 종료 가격 + (전일 최고가 - 전일 최저가) * K
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    # print("target_price", target_price)
    return target_price

def get_start_time(ticker) :
    """시작 시간 조회"""
    # 1일 기준 1개의 테이터
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    # print("df", df)

    # 시간 가져오기
    start_time = df.index[0]
    # print("start_time", start_time)
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker) :
    """잔고 조회 및 가져오기"""
    # 잔고 조회
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

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue

def get_ror(k=0.5, ticker="KRW-BTC") :
    # OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
    # 4시간 단위로 200개
    df = pyupbit.get_ohlcv(ticker, interval='minute60')
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    # 수수료
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
# 시작 메세지 슬랙 전송
# post_message(myToken, "#crypto", "autotrade start")

ticker = "KRW-BTC"

# predict_price(ticker)
# schedule.every().hour.do(lambda: predict_price(ticker))
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()                           # 현재 시간
        start_time = get_start_time(ticker)                     # 매매 시작 시간
        end_time = start_time + datetime.timedelta(days=1)      # 매매 종료 시간
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)     # 매수가
            current_price = get_current_price("KRW-BTC")        # 현재가
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)