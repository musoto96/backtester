#!bin/python3
import numpy as np
import pandas as pd


df18 = pd.read_csv('historical_data/2018XBTUSD1h.csv')
df18 = df18[::-1].reset_index(drop=True)


def moving_average_calculator(data, start=2, end=500):
    for i in range(start, end+1):
        data[str(i)] = np.nan
        for j in range(len(data)):
            data[str(i)][i+j-1] = np.mean(data['close'][j:i*(j+1)])
    return data


moving_average_calculator(df18).to_csv('historical_data/2018_ma_XBTUSD1h.csv', index=False)
