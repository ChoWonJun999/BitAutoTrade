import pyupbit
import matplotlib.pyplot as plt
from fbprophet import Prophet

"""
    이동평균선 테스트
"""

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute10")
# df = pyupbit.get_ohlcv("KRW-BTC", interval="minute10", count=11)
df.head()
df.tail()
# print(df)
ma5 = df['close'].rolling(window=5).mean()
ma10 = df['close'].rolling(window=10).mean()
# ma20 = df['close'].rolling(window=20).mean()
# ma60 = df['close'].rolling(window=60).mean()
# ma120 = df['close'].rolling(window=120).mean()
ma5 = ma5.reset_index()
ma10 = ma10.reset_index()
# ma20 = ma20.reset_index()
# ma60 = ma60.reset_index()
# ma120 = ma120.reset_index()

# plt.plot(df['close'], 'o-', label='Close')
ma5['sub'] = ma5['close'] - ma5['close'].shift(1)
ma10['sub'] = ma10['close'] - ma10['close'].shift(1)
print(ma5)
print(ma5.iloc[-1]['close'])
print(ma10.iloc[-1]['close'])
# print("max = ", abs(ma5['sub']).max())
# print("ave", abs(ma5['sub']).mean())
ma5.to_excel("ma5.xlsx")
ma10.to_excel("ma10.xlsx")

plt.plot(ma5['index'], ma5['close'], 'o-', label='Ma5')
plt.plot(ma10['index'], ma10['close'], 'o-', label='Ma10')
# plt.plot(ma20['index'], ma20['close'], label='Ma20')
# plt.plot(ma60['index'], ma60['close'], label='Ma60')
# plt.plot(ma120['index'], ma120['close'], label='Ma120')
plt.legend()
plt.show()