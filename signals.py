import functions as f
import MetaTrader5 as mt5

def signal1(df, balance, leverage, symbol):
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    lower, upper, middle, distance = f.BB(df, 100)

    stop_loss = None
    take_profit = None
    volume = None

    c1 = previous['ema_9'] <= latest['ema_9']
    c2 = latest['open'] < latest['close']
    c3 = previous['open'] > previous['close']
    c4  = latest['low'] < middle.iloc[-1]
    c5 = latest['open'] > middle.iloc[-1]
    c6 = latest['close'] < upper.iloc[-1]
    c7 = (latest['high'] - latest['low']) > (previous['high'] - previous['low'])
    c8 = latest['RSI'] > previous['RSI']
    c9 = previous['low'] < middle.iloc[-1]
    c10 = previous['high'] > middle.iloc[-1]
    c11 = previous['close'] < upper.iloc[-1]
    if all([c2, c4, c5, c6, c7, c8, c9, c10, c11]):
        signal = 'BUY'
    else:
        c1 = previous['ema_9'] >= latest['ema_9']
        c2 = latest['open'] > latest['close']
        c3 = previous['open'] < previous['close']
        c4 = latest['high'] > middle.iloc[-1]
        c5 = latest['open'] < middle.iloc[-1]
        c6 = latest['close'] > lower.iloc[-1]
        c7 = (latest['high'] - latest['low']) > (previous['high'] - previous['low'])
        c8 = latest['RSI'] < previous['RSI']
        c9 = previous['high'] > middle.iloc[-1]
        c10 = previous['low'] < middle.iloc[-1]
        c11 = previous['close'] > lower.iloc[-1]
        if all([c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]):
            signal = 'SELL'
        else:
            signal = None
    
    info = mt5.symbol_info(symbol)


    contract_size = info.trade_contract_size
    min_lot = info.volume_min
    lot_step =info.volume_step
    max_lot = info.volume_max

    risk = 0.1

    tp_multiplier = 3

    risk_amount = balance * risk

    volume = (risk_amount * leverage) / contract_size
    volume = max(min_lot, min(max_lot, round(volume / lot_step) * lot_step))

    if signal == 'BUY':
        stop_loss = min(df['open'].iloc[-5:-1])
        take_profit = df['close'].iloc[-1] + (df['close'].iloc[-1] - min(df['low'].iloc[-5:-1])) * tp_multiplier
    elif signal == 'SELL':
        stop_loss = max(df['open'].iloc[-5:-1]) 
        take_profit = df['close'].iloc[-1] - (max(df['high'].iloc[-5:-1]) - df['close'].iloc[-1]) * tp_multiplier

    return signal, stop_loss, take_profit, volume


def signal2(df, balance, leverage, symbol):
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    lower, upper, middle, distance = f.BB(df, 20)

    stop_loss = None
    take_profit = None
    volume = None


    #BUY condtions
    c1 = latest['close'] > latest['open']
    c2 = latest['low'] < middle.iloc[-1]
    c3 = latest['close'] > middle.iloc[-1]
    c4 = latest['low'] < latest['ema_21']
    c5 = latest['ema_21'] > previous['ema_21']
    c6 = previous['open'] > previous['close']
    c7 = previous['low'] > middle.iloc[-1]
    c8 = (latest['high'] - latest['low']) > (previous['high'] - previous['low'])
    if all([c1, c2, c3, c4, c5, c6, c7, c8]):
        signal = 'BUY'
    else:
        #SELL condtions
        c1 = latest['close'] > latest['open']
        c2 = latest['high'] > middle.iloc[-1]
        c3 = latest['close'] < middle.iloc[-1]
        c4 = latest['low'] > latest['ema_21']
        c5 = latest['ema_21'] > previous['ema_21']
        c6 = previous['open'] < previous['close']
        c7 = previous['high'] < middle.iloc[-1]
        c8 = (latest['high'] - latest['low']) > (previous['high'] - previous['low'])
        if all([c1, c2, c3, c4, c5, c6, c7, c8]):
            signal = 'SELL'
        else:
            signal = None

    info = mt5.symbol_info(symbol)


    contract_size = info.trade_contract_size
    min_lot = info.volume_min
    lot_step =info.volume_step
    max_lot = info.volume_max

    risk = 0.1

    tp_multiplier = 5

    risk_amount = balance * risk

    volume = (risk_amount * leverage) / contract_size
    volume = max(min_lot, min(max_lot, round(volume / lot_step) * lot_step))

    if signal == 'BUY':
        stop_loss = min(df['open'].iloc[-5:-1])
        take_profit = df['close'].iloc[-1] + (df['close'].iloc[-1] - min(df['close'].iloc[-10:-1])) * tp_multiplier
    elif signal == 'SELL':
        stop_loss = max(df['open'].iloc[-5:-1]) 
        take_profit = df['close'].iloc[-1] - (max(df['open'].iloc[-10:-1]) - df['close'].iloc[-1]) * tp_multiplier

    return signal, stop_loss, take_profit, volume

def signal3(df, balance, leverage, symbol):
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    stop_loss = None
    take_profit = None
    volume = None

    if latest['macd_h'] < 0:
        c1 = previous['RSI'] < latest['RSI']
        c2 = previous['close'] < previous['open']
        c3 = latest['close'] > latest['open']
        c4 = all(x < 0 for x in df['macd_h'].iloc[-8:-2])
        if all([c1, c2, c3, c4]):
            signal = 'BUY'
        else:
            signal = None
    elif latest['macd_h'] > 0:
        c1 = previous['RSI'] > latest['RSI']
        c2 = previous['close'] > previous['open']
        c3 = latest['close'] < latest['open']
        c4 = all(x < 0 for x in df['macd_h'].iloc[-8:-2])
        if all([c1, c2, c3, c4]):
            signal = 'SELL'
        else:
            signal = None
    else:
        signal = None

    info = mt5.symbol_info(symbol)

    contract_size = info.trade_contract_size
    min_lot = info.volume_min
    lot_step =info.volume_step
    max_lot = info.volume_max

    risk = 0.1

    tp_multiplier = 3

    point = info.point
    atr_price = df['ATR'].iloc[-1] * point * 10

    risk_amount = balance * risk

    volume = (risk_amount * leverage) / contract_size
    volume = max(min_lot, min(max_lot, round(volume / lot_step) * lot_step))

    if signal == 'BUY':
        stop_loss = latest['close'] - atr_price
        take_profit = latest['close'] + atr_price * tp_multiplier
    elif signal == 'SELL':
        stop_loss = latest['close'] + atr_price
        take_profit = latest['close'] - atr_price * tp_multiplier

    return signal, stop_loss, take_profit, volume
