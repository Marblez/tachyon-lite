import numpy as np
import pandas as pd
from binance.client import Client
import math
import os.path
import time
from datetime import timedelta, datetime
from dateutil import parser

# Constants
binance_api_key = '25HUOrJu76evPWNCJtSDydExaKtdB6DjyItVW5lTYSzEe2NgAvMsfLfuuX8Ake1m'
binance_api_secret = 'vBaUNet4o7N2qVA3lW84Is6RXFnAt4Q6Dk6qdfiR1VzAOi0vO4Ujq2eCq0qHjCfP'
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)

def kelly(win_rate, win_amount, loss_amount):
	if win_amount == 0:
	    return -0.8
	if loss_amount == 0:
	    return 0.8
	kelly = win_rate - ((1-win_rate) / (win_amount/loss_amount));
	if kelly > 0.8:
		return 0.8
	elif kelly < -0.8:
		return -0.8
	return kelly
    
def minutes_of_new_data(symbol, kline_size, data, source):
	if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
	elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')
	if source == "binance": new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
	return old, new

def get_all_binance(symbol, kline_size, save = False):
	filename = '%s-%s-data.csv' % (symbol, kline_size)
	if os.path.isfile(filename): data_df = pd.read_csv(filename)
	else: data_df = pd.DataFrame()
	oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source = "binance")
	delta_min = (newest_point - oldest_point).total_seconds()/60
	available_data = math.ceil(delta_min/binsizes[kline_size])
	if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'): print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
	else: print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
	klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
	data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
	data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
	if len(data_df) > 0:
		temp_df = pd.DataFrame(data)
		data_df = data_df.append(temp_df)
	else: data_df = data
	data_df.set_index('timestamp', inplace=True)
	if save: data_df.to_csv(filename)
	print('All caught up..!')
	return data_df
