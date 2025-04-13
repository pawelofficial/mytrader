import ms 
import requests 
import pandas as pd 
import time 
import datetime
import requests
import logging 
import dotenv
import os
dotenv.load_dotenv()

logger=logging.getLogger('trade_5m')
logger.setLevel(logging.INFO)
# add file handler 
fh = logging.FileHandler('trade_5m.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)


logger.info('trade_5m started')
print('running')

d=ms.data.Data()
INTERVAL='30m'
N=1000
dic={'comment':'','datetime':'','signal':'','last_order':'', 'candle':'','action':'','amos':'','order':''}
trade_df=pd.DataFrame(columns=dic.keys())
delta=d.get_time_to_candle_close(interval=INTERVAL)
print(delta)
s=ms.strategy.Strategy(d)
tb=ms.trade_binance.Trade()
# sell everything 
o,amos=tb.sell('bitek',-1)


btc=tb.get_balance('BTC')
usdt=tb.get_balance('USDT')

logger.info('starting balance: ')
logger.info(f'usdt:{usdt},btc:{btc}')


def sleep_with_countdown(total_seconds):
    total_seconds = int(total_seconds)
    for remaining in range(total_seconds, 0, -1):
        print(f"\rSleeping... {remaining} sec remaining", end="", flush=True)
        time.sleep(1)
    print("\rDone sleeping!")

def optimize():
    d.get_binance_candles('BTCUSDT',interval=INTERVAL,limit=N)
    d.recalculate_all()
    s=ms.strategy.Strategy(d)
    dic=s.optimize()
    param=dic['params']
    logger.info(f'optimized params {dic}')
    return param

PARAM=0
count=0
is_starting=True    
while True:
    if count > 2 or is_starting:
        logger.info('optimizing')
        PARAM=optimize()
        count=0
        is_starting=False
    
    delta=d.get_time_to_candle_close(interval=INTERVAL)
    if delta > 5 :
        logger.info(f'sleeping {delta-5.1}')
        print(f'sleeping {delta-5.1}')
        sleep_with_countdown(delta-5.1)
        
    else:
        dic['datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        count+=1
        logger.info('time to trade ! ')
        last_candle=d.get_last_candle(interval=INTERVAL)
        dic['candle']=str(last_candle.to_dict())
        
        logger.info(f'last candle {last_candle}')
        d.delsert_df(last_candle)
        d.recalculate_all()
        sig=s.strategy(params=[PARAM],save=True)
        bl=sig.iloc[-1]       
        dic['signal']=bl
        
        logger.info(f'signal {bl}, last_order {tb.last_order}')
        if bl==1:
            if tb.last_order['side']=='SELL':
                dic['action']='buy'
                logger.info('----> buying')
                o,amos=tb.buy('bitek', 20)
                dic['order']=str(o)
                dic['amos']=str(amos)
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
                dic['order']='bought'
            else:
                dic['comment']='no position to buy'
                logger.info('----> no position to buy')
        if bl==0:
            
            if tb.last_order['side']=='BUY':
                dic['action']='sell'
                logger.info('----> selling')
                o,amos=tb.sell('bitek',-1)
                dic['order']=str(o)
                dic['amos']=str(amos)
                dic['order']='sold'
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
            else:
                dic['comment']='no position to sell'
                logger.info('----> no position to sell')    
        trade_df.loc[len(trade_df)]=dic
        dic={}
        print(trade_df)
        trade_df.to_csv('trade_5m.csv',sep='|')
        time.sleep(6)
