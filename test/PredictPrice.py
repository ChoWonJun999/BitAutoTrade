import pyupbit
import datetime
from fbprophet import Prophet
import matplotlib.pyplot as plt

"""
    predict price
    test
"""

predicted_close_price = 0
df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60")
df = df.reset_index()
print("df.reset_index() = ", df.reset_index())
df['ds'] = df['index']
df['y'] = df['close']
data = df[['ds','y']]
model = Prophet()
model.daily_seasonality = True
model.weekly_seasonality = True
model.yearly_seasonality = True
model.fit(data)
future = model.make_future_dataframe(periods=4, freq='H')
forecast = model.predict(future)

"""
fig1 = model.plot(forecast)
fig2 = model.plot_components(forecast)
fig1.show()
fig2.show()
"""

endHour = 0
now = datetime.datetime.now()
if(now.hour%4 == 0) : endHour = now.hour+1
elif(now.hour%4 == 1) : endHour = now.hour
elif(now.hour%4 == 2) : endHour = now.hour+3
else : endHour = now.hour+2
closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=endHour)]
if len(closeDf) == 0:
    closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=endHour)]
closeValue = closeDf['yhat'].values[0]
predicted_close_price = closeValue

# print(forecast['yhat'])
# plt.plot(forecast['yhat'])
# plt.show()
# forecast.to_excel("forecast.xlsx")
# print(forecast)
# print(forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=endHour))