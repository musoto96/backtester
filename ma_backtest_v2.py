#!bin/python3
import numpy as np
import pandas as pd


def crossover_backtest(df):
    print(df.head)


data = pd.read_csv("historical_data/2018_ma_XBTUSD1h.csv")
crossover_backtest(data)
