import pyupbit
import numpy as np

"""
    Back-Testing
    test
"""

# OHLCV(open, high, low, close, volume)로 당일 시가, 고가, 저가, 종가, 거래량에 대한 데이터
# df = pyupbit.get_ohlcv("KRW-BTC", count=7)
 # 4시간 단위로 7일치
df = pyupbit.get_ohlcv("KRW-BTC", interval='minute240', count=62)
# print(df)

# 변동폭 * K 계산, (고가 - 저가) * k값
df['range'] = (df['high'] - df['low']) * 0.5
# print(df)

# target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target'] = df['open'] + df['range'].shift(1)
# print(df)

# 수수료
fee = 0.0005
# row(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
# print(df)

# 누적 곱 계산(cumprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()
# print(df)

# Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
# print(df)

# MDD(Max DrawDown) 계산
print("MDD(%) = ", df['dd'].max())

df = df.rename(mapper={'open':'open(시가)'
                , 'high':'high(고가)'
                ,'low':'low(저가)'
                ,'close':'close(종가)'
                ,'volume':'volume(거래량)'
                ,'value':'value'
                , 'range':'range(변동폭*k)'
                , 'target':'target(매수가)'
                , 'ror':'ror(수익률)'
                , 'hpr':'hpr(누적 수익률)'
                , 'dd':'dd(낙폭률)'}, axis=1)

#엑셀로 출력
df.to_excel("dd.xlsx")