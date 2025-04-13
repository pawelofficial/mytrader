import ms
import requests
import pandas as pd
import time
import datetime
import logging
import dotenv
import os

dotenv.load_dotenv()

logger = logging.getLogger('trade_5m')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('trade_5m.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

logger.info('trade_5m started')

d = ms.data.Data()
INTERVAL = '5m'
N = 1000



# Define clear columns for the trade log
columns = ['Timestamp',  'Signal', 'Action','Asset','Trade_amount',  'Amos', 'Comment','Candle','Order', 'Last Order']
trade_df = pd.DataFrame(columns=columns)

delta = d.get_time_to_candle_close(interval=INTERVAL)
print(delta)
s = ms.strategy.Strategy(d)
tb = ms.trade_binance.Trade()

# Sell everything initially
o, amos = tb.sell('bitek', -1)
btc = tb.get_balance('BTC')
usdt = tb.get_balance('USDT')
logger.info('starting balance:')
logger.info(f'usdt: {usdt}, btc: {btc}')

def sleep_with_countdown(total_seconds):
    total_seconds = int(total_seconds)
    for remaining in range(total_seconds, 0, -1):
        print(f"\rSleeping... {remaining} sec remaining", end="", flush=True)
        time.sleep(1)
    print("\rDone sleeping!")

def optimize():
    d.get_binance_candles('BTCUSDT', interval=INTERVAL, limit=N)
    d.recalculate_all()
    strat = ms.strategy.Strategy(d)
    opt_dic = strat.optimize()
    param = opt_dic['params']
    logger.info(f'optimized params {opt_dic}')
    return param

PARAM = 0
count = 0
is_starting = True

while True:
    if count > 2 or is_starting:
        logger.info('optimizing')
        PARAM = optimize()
        count = 0
        is_starting = False

    delta = d.get_time_to_candle_close(interval=INTERVAL)
    if delta > 5:
        logger.info(f'sleeping {delta - 5.1}')
        print(f'sleeping {delta - 5.1}')
        sleep_with_countdown(delta - 5.1)
    else:
        count += 1
        # Build a clear log row for the trade
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_candle = d.get_last_candle(interval=INTERVAL)
        candle_info = last_candle.to_dict()
        row = {
            'Timestamp': timestamp,
            'Signal': None,
            'Action': None,
            'Amos': None,
            'trade_amount': None,
            'price': -1,
            'Comment': "",
            'Candle': candle_info,
            'Order': None,
            'Last Order': str(tb.last_order)
        }
        
        logger.info('time to trade!')
        logger.info(f'last candle: {candle_info}')
        
        d.delsert_df(last_candle)
        d.recalculate_all()
        sig = s.strategy(params=[PARAM], save=True)
        bl = sig.iloc[-1]
        row['Signal'] = bl
        logger.info(f'signal {bl}, last_order {tb.last_order}')
        
        if bl == 1:
            if tb.last_order['side'] == 'SELL':
                row['Action'] = 'BUY'
                logger.info('----> buying')
                o, amos = tb.buy('bitek', 20)
                row['Order'] = str(o)
                row['Amos'] = str(amos)
                row['trade_amount'] = o['cummulativeQuoteQty']
                row['price']=last_candle['close']
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
            else:
                row['Comment'] = 'No position to buy'
                logger.info('----> no position to buy')
        elif bl == 0:
            if tb.last_order['side'] == 'BUY':
                row['Action'] = 'SELL'
                logger.info('----> selling')
                o, amos = tb.sell('bitek', -1)
                row['Order'] = str(o)
                row['Amos'] = str(amos)
                row['trade_amount'] = o['cummulativeQuoteQty']
                row['price']=last_candle['close']
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
            else:
                row['Comment'] = 'No position to sell'
                logger.info('----> no position to sell')
        
        trade_df.loc[len(trade_df)] = row
        print(trade_df.to_string(index=False))
        trade_df.to_csv('trade_5m.csv', sep='|', index=False)
        time.sleep(6)
