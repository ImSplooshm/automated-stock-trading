import MetaTrader5 as mt5
import time
from tqdm import tqdm
import backtest as b
import signals as s
import functions as f
import tkinter as tk

if __name__ == '__main__':
    username = None
    password = None
    server = None

    mt5.initialize(path="C:/Program Files/MetaTrader 5/terminal64.exe", timeout=180000)
    mt5.login(username, password, server)

    info = mt5.account_info()

    symbols = mt5.symbols_get()
    stocks = [symbol.name for symbol in symbols if "FOREX" in symbol.path.upper()]

    time_live = 0

    while mt5.last_error() == 1:
        balance = info.balance()
        leverage = info.leverage()
        period = mt5.TIMEFRAME_M1
        n = 200

        for ticker in tqdm(stocks):
            df = b.data(ticker, n, period)
            signal, stop_loss, take_profit, volume = s.signal1(df, balance, leverage, ticker)
            if signal != None:
                type = mt5.ORDER_TYPE_BUY if signal =='BUY' else mt5.ORDER_TYPE_SELL

                f.PURCHASE(symbol = ticker,
                           type = type,
                           tp = take_profit,
                           sl = stop_loss,
                           volume = volume
                        )
        
        time.sleep(59)
        time_live += 1
        print(f'Time live: {time_live} {period}')
