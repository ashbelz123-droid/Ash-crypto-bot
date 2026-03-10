# bot.py

import ccxt, time, pandas as pd, pandas_ta as ta
from utils import send_telegram, start_heartbeat
from config import *

# ---------------- INIT ----------------
exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# Set leverage for all symbols
for symbol in TRADING_SYMBOLS:
    exchange.set_leverage(LEVERAGE, symbol)

STARTING_BALANCE = exchange.fetch_balance()['USDT']['free']
DAILY_LOSS_LIMIT = STARTING_BALANCE * DAILY_LOSS_LIMIT_PERCENT / 100

# Start heartbeat ping
start_heartbeat()

# ---------------- MARKET DATA ----------------
def get_ohlcv(symbol):
    candles = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=200)
    df = pd.DataFrame(candles, columns=['time','open','high','low','close','volume'])
    df['ema50'] = ta.ema(df['close'],50)
    df['ema200'] = ta.ema(df['close'],200)
    df['rsi'] = ta.rsi(df['close'],14)
    df['atr'] = ta.atr(df['high'], df['low'], df['close'],14)
    df['vol_avg'] = df['volume'].rolling(20).mean()
    return df

def higher_trend(symbol):
    candles = exchange.fetch_ohlcv(symbol, '1h', limit=200)
    df = pd.DataFrame(candles, columns=['time','open','high','low','close','volume'])
    df['ema200'] = ta.ema(df['close'],200)
    return "UP" if df['close'].iloc[-1] > df['ema200'].iloc[-1] else "DOWN"

# ---------------- SIGNALS ----------------
def check_long_signal(df, symbol):
    last = df.iloc[-1]
    return all([
        higher_trend(symbol) == "UP",
        35 < last['rsi'] < 50,
        last['close'] <= last['ema50']*1.01,
        last['volume'] > last['vol_avg']*1.2,
        last['close'] > last['open']
    ])

def check_short_signal(df, symbol):
    last = df.iloc[-1]
    return all([
        higher_trend(symbol) == "DOWN",
        50 < last['rsi'] < 65,
        last['close'] >= last['ema50']*0.99,
        last['volume'] > last['vol_avg']*1.2,
        last['close'] < last['open']
    ])

# ---------------- POSITION SIZE ----------------
def calculate_position(df, direction, symbol):
    last_price = df['close'].iloc[-1]
    atr = df['atr'].iloc[-1]
    if direction=="LONG":
        sl = last_price - atr*1.5
        tp = last_price + atr*2.5
    else:
        sl = last_price + atr*1.5
        tp = last_price - atr*2.5

    position_size = MAX_LOSS / abs(last_price - sl)
    position_size = max(position_size, MIN_CONTRACT)
    max_position_size = exchange.fetch_balance()['USDT']['free'] * LEVERAGE
    position_size = min(position_size, max_position_size)

    return position_size, sl, tp, last_price

# ---------------- TRADE MONITOR ----------------
def monitor_trade(direction, entry_price, sl, tp, amount, symbol):
    df = get_ohlcv(symbol)
    atr = df['atr'].iloc[-1]
    while True:
        ticker = exchange.fetch_ticker(symbol)
        last_price = ticker['last']

        # ATR trailing stop
        if direction=="LONG" and last_price-entry_price > atr*0.5:
            sl = max(sl, last_price - atr*1.0)
        if direction=="SHORT" and entry_price-last_price > atr*0.5:
            sl = min(sl, last_price + atr*1.0)

        # Stop-loss
        if (direction=="LONG" and last_price <= sl) or (direction=="SHORT" and last_price >= sl):
            if direction=="LONG": exchange.create_market_sell_order(symbol, amount)
            else: exchange.create_market_buy_order(symbol, amount)
            send_telegram(f"⚠️ Stop-loss hit! {symbol} {direction} closed at {last_price}")
            return False

        # Take-profit
        if (direction=="LONG" and last_price >= tp) or (direction=="SHORT" and last_price <= tp):
            if direction=="LONG": exchange.create_market_sell_order(symbol, amount)
            else: exchange.create_market_buy_order(symbol, amount)
            send_telegram(f"✅ Take-profit hit! {symbol} {direction} closed at {last_price}")
            return True

        time.sleep(1)

# ---------------- DAILY LOSS ----------------
def check_daily_loss():
    current_balance = exchange.fetch_balance()['USDT']['free']
    if current_balance <= STARTING_BALANCE - DAILY_LOSS_LIMIT:
        send_telegram(f"⚠️ Daily loss limit reached ({DAILY_LOSS_LIMIT:.3f}). Bot paused until next day.")
        return True
    return False

# ---------------- MAIN LOOP ----------------
def main():
    while True:
        try:
            if check_daily_loss():
                time.sleep(60*60)  # pause 1 hour
                continue

            for symbol in TRADING_SYMBOLS:
                # Skip if open positions exist
                positions = exchange.fetch_positions()
                if any(p['symbol']==symbol.replace("/","") and float(p['contracts'])>0 for p in positions):
                    continue

                df = get_ohlcv(symbol)

                if check_long_signal(df, symbol):
                    amount, sl, tp, entry_price = calculate_position(df,"LONG", symbol)
                    exchange.create_market_buy_order(symbol, amount)
                    send_telegram(f"✅ {symbol} LONG opened: Entry {entry_price}, SL {sl}, TP {tp}")
                    monitor_trade("LONG", entry_price, sl, tp, amount, symbol)

                elif check_short_signal(df, symbol):
                    amount, sl, tp, entry_price = calculate_position(df,"SHORT", symbol)
                    exchange.create_market_sell_order(symbol, amount)
                    send_telegram(f"✅ {symbol} SHORT opened: Entry {entry_price}, SL {sl}, TP {tp}")
                    monitor_trade("SHORT", entry_price, sl, tp, amount, symbol)

            time.sleep(10)

        except Exception as e:
            send_telegram(f"❌ Error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
