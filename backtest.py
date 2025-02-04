import functions as f
import MetaTrader5 as mt5
import pandas as pd
import os
import json
from datetime import datetime
from tqdm import tqdm
import math
import signals as s

def data(symbol, n, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['ema_9'] = f.EMA(df['close'], 9)
    df['ema_5'] = f.EMA(df['close'], 5)
    df['ema_21'] = f.EMA(df['close'], 21)
    df['ema_35'] = f.EMA(df['close'], 35)
    df['ema_50'] = f.EMA(df['close'], 50)
    df['macd'] = df['ema_5'] - df['ema_35']
    df['vma'] = f.EMA(df['tick_volume'], 35)
    df['macd_signal'] = f.EMA(df['macd'], 5)
    df['macd_h'] = df['macd'] - df['macd_signal']

    df['RSI'] = f.RSI(df['close'], 14)

    df['ATR'] = f.ATR(df, 14)

    return df

def saveData():
    symbols = mt5.symbols_get()
    tickers = [symbol.name for symbol in symbols if "FOREX" in symbol.path.upper()]

    n = 2000
    timeframe = mt5.TIMEFRAME_M1

    path = f'data/{str(n)}+{str(timeframe)}/'

    if not os.path.exists(path):
        os.makedirs(path)

    params = {
        'num':len(tickers),
        'period': n,
        'interval': timeframe,
        'datetime': str(datetime.now())
    }

    with open(f'{path}data.json', 'w') as json_file:
        json.dump(params, json_file, indent=4)

    for ticker in tqdm(tickers):
        df = data(ticker, n, timeframe)
        df.to_csv(f'{path}{ticker}.csv')


def backtest():
    balance = 1000
    initial_balance = balance

    risk = 0.1

    trades = 0
    profitable_trades = 0


    symbols = mt5.symbols_get()
    tickers = [symbol.name for symbol in symbols if "FOREX" in symbol.path.upper()]
    tickers = tickers[:30]

    n = 2000
    timeframe = mt5.TIMEFRAME_M1

    path = f'data/{str(n)}+{str(timeframe)}/'

    for ticker in tqdm(tickers):
        if balance < initial_balance * 0.001:
            print('Loop closed due to insufficient funds')
            break

        current_trade = None
        try:
            main_df = pd.read_csv(f'{path}{ticker}.csv')
        except FileExistsError:
            print(f'File not found, ticker: {ticker}')

        for i in tqdm(range(5, len(main_df))):
            df = main_df[:i]
            signal, sl, tp, volume = s.signal3(df = df,
                                               balance = balance,
                                               leverage = 500,
                                               symbol = ticker)
            volume = risk * balance

            if current_trade == None and signal != None:
                trades += 1
                if signal == 'BUY':
                    current_trade = {
                            'type': 'LONG',
                            'entry_price': df['close'].iloc[-1],
                            'stop_loss': sl,
                            'take_profit': tp,
                            'position_size': (df['close'].iloc[-1] / volume),
                            'entry_index': i,
                        }
                elif signal == 'SELL':
                    current_trade = {
                            'type': 'SHORT',
                            'entry_price': df['close'].iloc[-1],
                            'stop_loss': sl,
                            'take_profit': tp,
                            'position_size': (df['close'].iloc[-1] / volume),
                            'entry_index': i,
                        }
            elif current_trade != None:
                if df['close'].iloc[-1] <= current_trade['stop_loss'] and current_trade['type'] == 'LONG':
                        loss = current_trade['position_size'] * (current_trade['entry_price'] - current_trade['stop_loss'])
                        balance -= loss

                        current_trade = None 
                elif df['close'].iloc[-1] >= current_trade['take_profit'] and current_trade['type'] == 'LONG':
                        profit = current_trade['position_size'] * (current_trade['take_profit'] - current_trade['entry_price'])
                        balance += profit

                        current_trade = None
                        profitable_trades += 1
                elif df['close'].iloc[-1] >= current_trade['stop_loss'] and current_trade['type'] == 'SHORT':
                    loss = current_trade['position_size'] * (current_trade['entry_price'] - current_trade['stop_loss'])
                    balance -= loss

                    current_trade = None
                elif df['close'].iloc[-1] <= current_trade['take_profit'] and current_trade['type'] == 'SHORT':
                    profit = current_trade['position_size'] * (current_trade['take_profit'] - current_trade['entry_price'])
                    balance += profit

                    profitable_trades += 1
                    current_trade = None
            df = main_df

    overall_return = (balance - initial_balance) / initial_balance * 100
    profitable_percentage = profitable_trades / trades * 100
    avg_return = math.log(overall_return, trades) if overall_return > 0 else None
    
    results = {
        'initial balance': initial_balance,
        'resulting balance': balance,
        'trades': trades,
        'return': overall_return,
        'average return': avg_return,
        'success rate': profitable_percentage
    }

    return results


if __name__ == '__main__':
    mt5.initialize()
    results = backtest()
    print(mt5.last_error())
    print(results)
