#!bin/python3
import numpy as np
import pandas as pd
import json


class Portfolio:
    def __init__(self, balance, fee, slip, tp, sl, fixed=True):
        self.balance = balance
        self.fee = fee
        self.slip = slip
        self.tp = tp
        self.sl = sl
        self.fixed = fixed
        self.pnl = 0
        self.trades = 0

    def results(self):
        print(f'Balance: {round(self.balance, 2)}\nFee: {self.fee}\nSlip: {self.slip}\nTake-profit: {self.tp}\nStop-loss: {self.sl}\nFixed: {self.fixed}\nPnl: {round(self.pnl*100, 2)}%\nTrades: {self.trades}\n')


class Mac:
    def __init__(self, history, data = {}):
        self.history = history
        self.f = data['fast']
        self.s = data['slow']
        self.old = ''
        self.new = ''

    def signal(self, portfolio, test=False, start = 0, end = 0, position='', pos_open=0):
        if test == False:
            timestamps = self.history.loc[:, 'timestamp']
            closes = self.history.loc[:, 'close']
        else:
            cutHistory = self.history.iloc[start:end, :]
            timestamps = cutHistory.loc[:, 'timestamp']
            closes = cutHistory.loc[:, 'close']

        signal = ''
        subsignal = ''
        timestamp = ''
        price = 0

        fma = np.mean(closes.iloc[:self.f])
        sma = np.mean(closes.iloc[:self.s])

        if fma < sma:
            self.new = 'short'
        elif fma > sma:
            self.new = 'long'

        if position != '':
            pnl = (closes.iloc[0] - pos_open) / pos_open

            if position == 'short':
                pnl = -pnl

            if pnl >= portfolio.tp or pnl <= -portfolio.sl:
                if pnl >= portfolio.tp:
                    subsignal = 'takeProfit'
                elif pnl <= -portfolio.sl:
                    subsignal = 'stopLoss'

                if position == 'short':
                    signal = 'long'
                else:
                    signal = 'short'

                position = ''
                timestamp = timestamps.iloc[0]
                price = closes.iloc[0]

        if self.old != '' and self.new != '':
            if self.new != self.old: 
                signal = self.new
                self.old = self.new
                position = self.new
                timestamp = timestamps.iloc[0]
                price = closes.iloc[0]

        elif self.old == '':
            self.old = self.new
        
        return {
                "signal": signal,
                "subsignal": subsignal,
                "timestamp": timestamp,
                "pos": position,
                "price": price
                }

    def historic(self, portfolio):

        signals = []
        pos = ''
        pos_open = 0

        for i in range(len(self.history) - self.s):
            start = len(self.history)-i-1-self.s
            end = len(self.history)-i-1

            bt = self.signal(portfolio, 
                    test=True, 
                    start=start, 
                    end=end,
                    position=pos,
                    pos_open=pos_open)

            if bt['signal'] != '':
                if bt['subsignal'] == '':
                    pos = bt['pos']
                    pos_open = bt['price']
                else:
                    pos = ''
                    pos_open = 0

                signals.append({'signal': bt['signal'], 
                    'subsignal': bt['subsignal'], 
                    'timestamp': bt['timestamp'], 
                    'price': bt['price']})

        return signals


def backtest(history, portfolio, strategy, data, quiet=True):
    test = strategy(history, data)
    btsignals = test.historic(portfolio)
    
    position = {}
    total_pnl = 0
    balance = portfolio.balance

    for i in btsignals:
        if i['signal'] == 'short':
            i['price'] = i['price'] * ( 1 - portfolio.slip)
        elif i['signal'] == 'long':
            i['price'] = i['price'] * ( 1 + portfolio.slip)

        if not portfolio.fixed:
            balance = portfolio.balance
        
        new_position = i

        if position == {}:
            portfolio.balance -= balance * portfolio.fee
            position = new_position
            if quiet != True:
                print(position, '\n', portfolio.balance, ': ', balance, '\n')
        else:
            pnl = (new_position['price'] - position['price']) / position['price']

            if position['signal'] == 'short':
                pnl *= -1

            total_pnl += pnl
            portfolio.balance += balance * pnl
            portfolio.balance -= balance * portfolio.fee

            if new_position['subsignal'] != '':
                if quiet != True:
                    print(new_position)
                position = {}
            else:
                position = new_position
                if quiet != True:
                    print(position)

            if quiet != True:
                print(pnl, '\n', portfolio.balance, ': ', balance, '\n')

    portfolio.pnl = total_pnl
    portfolio.trades = len(btsignals)
    portfolio.results()



prices = pd.read_csv('historical_data/257001hXBTUSD.csv')

#####################
#   DOCUMENTACIÓN   #
#####################

####   TRADING    ###################################################################
#
# Sea el promedio rapido "fma" y el promedio lento "sma"
#  Si fma pasa de:  
#       fma < sma
#           a
#       fma > sma   
#   Es señal de compra. Si se tenia short abierto, se cierra el short y se abre long.
#
#  Si fma pasa de:  
#       fma > sma
#           a
#       fma < sma   
#   Es señal de venta. Si se tenia long abierto, se cierra el long y se abre short.
# 
#  Si en cualquier momento la perdida llega a 1.5% se cierra la posición y se espera
#   una nueva señal.
#
#####################################################################################


####   USO DEL PROGRAMA    ##########################################################
#
# margin:               Tamaño de posición (default 100 USD).
# slippage              No implementado.
# take-profit:          Toma de ganancia (default 50%).
# stop-loss:            Corte de pérdidas (default 1.5%).
# fee:                  Comisión (0.1% en Binance) (default 0.1%).
# fixed:                True si el tamaño de posición sera el mismo, 
#                         False si el tamaño de posición se acumula.
#
#####################################################################################

####   LECTURA DE RESULTADOS    #####################################################
#
# Balance:              Balance final
# Fee                   Comisión utilizada en la prueba
# Take-profit:          Toma de ganancia utilizada.
# Stop-loss:            Corte de pérdidas utilizado.
# Fixed:                Si utilizó posición fija o acumulada
# Pnl:                  Porcentaje de ganancia/perdida (perdida si es negativo).
# Trades:               Numero de posiciones abiertas.
#
#####################################################################################




my_portfolio = Portfolio(balance = 100,
        fee = 0.001,
        slip = 0.0,
        tp = 0.50, 
        sl = 0.015,
        fixed = True)

# fast-ma: 48; slow-ma: 128
backtest(prices, my_portfolio, Mac, {'fast': 48, 'slow': 128})

