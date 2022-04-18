from urllib.parse import urlencode
import pandas as pd
import pyupbit
import requests
import numpy as np

"""
    거래정보
    test
    현재 실패 후 거래 도중 엑셀에 데이터 추가
"""

access = "CR3vYIFTqY2bhXpJ8AU8OK8YrlDCwYq3dkutsHM4"
secret = "PPPxxTjZG1LWPRqeTg5xoQGEsSVpr1DnqxUW1Qxx"

upbit = pyupbit.Upbit(access, secret)

# data = pd.DataFrame(upbit.get_deposit_withdraw_status())
# print(data)

import requests

url = "https://api.upbit.com/v1/trades/ticks?market=KRW-BTC&count=10"

headers = {"Accept": "application/json"}

response = requests.request("GET", url, headers=headers)

data = pd.DataFrame(response.json())
data['ask_bid'] = np.where(data['ask_bid'] == "BID", "매도", "매수")
# print(data)
# print(data['ask_bid'])
print(upbit.get_individual_order("KRW-BTC"))