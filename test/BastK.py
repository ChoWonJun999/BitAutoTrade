import pyupbit
import numpy as np

"""
    best k 값 찾기
    test
"""

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", interval='minute240', count=62)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.9995
    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] * fee, 1)
    print("----------------", k, "----------------")
    print(df)
    ror = df['ror'].cumprod()[-2]
    return ror

bestk = 0.0
bestror = 0.0
for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    if bestror < ror :
        bestror = ror
        bestk = k
    # print("%.1f %f" % (k, ror))

print("%.1f %f" % (bestk, bestror))

# df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=2)
# print(df)
# print(df.iloc[0])