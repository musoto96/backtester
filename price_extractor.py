import numpy as np
import pandas as pd
import bitmex
import json
import datetime
import logging
import math
from time import sleep
import importlib

# Edit credentials file with your api keys
credentials = importlib.import_module('api_credentials')

client = bitmex.bitmex(test=False, api_key=credentials.api_key, 
	api_secret=credentials.api_secret)

# Set number of results, ie 9000 hours for +1 year of data
n = 25700
sym = 'XBTUSD'
period = '1h' # 1m, 5m, 4h, etc.

raw_pages = []
for i in range(n//500 + 1):
	page = client.Trade.Trade_getBucketed(symbol=sym,binSize=period, 
		count=500, start=500*i, reverse=True).result()[0]

	print(i)
	raw_pages.append(page)
	sleep(2)


pages = []
for i in range(len(raw_pages)):
	df_page = pd.DataFrame(raw_pages[i])
	pages.append(df_page)


df = pd.concat(pages)
df = df.reset_index(drop=True)
#print(df)
name = str(n)+period+sym+'.csv'

df.to_csv(f'historical_data/{name}', index=False)

