import pyupbit
import numpy as np
import matplotlib.pyplot as plt

"""
    plot test
"""

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute240", count=62)
df['range'] = (df['high'] - df['low']) * 0.5
df['target'] = df['open'] + df['range'].shift(1)
fee = 0.0005
df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1)
df['hpr'] = df['ror'].cumprod()
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
print(df)
plt.plot(df['ror'], 'bo-')
plt.grid(True)
plt.show()
# print("MDD(%) = ", df['dd'].max())