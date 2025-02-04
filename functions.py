from ta.momentum import RSIIndicator
import MetaTrader5 as mt5

def RSI(df, n):
    rsi = RSIIndicator(df, n).rsi()
    return rsi

def EMA(df, n):
    ema = df.ewm(span=n, adjust = False).mean()
    return ema

def ATR(df, n):
    df['h-l'] = df['high'] - df['low']
    df['h-c'] = df['high'] - df['close'].shift().abs()
    df['l-c'] = df['low'] - df['close'].shift().abs()

    df['tr'] = df[['h-l','h-c','l-c']].max(axis=1)

    atr = EMA(df['tr'], n)

    return atr

def BB(df, n):
    prices = df['close']
    middle = prices.rolling(window = n).mean()
    std_dev = prices.rolling(window = n).std()
    upper = middle + (2 * std_dev)
    lower = middle - (2 * std_dev)
    distance = (upper - lower).abs()
    return lower, middle, upper, distance

def PURCHASE(symbol, type, tp, sl, volume):

    price = mt5.symbol_info_tick(symbol)
    price = price.ask
    
    request = {
        'action':mt5.TRADE_ACTION_DEAL,
        'symbol':symbol,
        'volume':volume,
        'type':type,
        'price':price,
        'sl':sl,
        'tp':tp,
        'deviation':20,
        'magic': 12345678,
        'comment':'Python script open',
        'type_time':mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC
    }

    result = mt5.order_send(request)
    return result