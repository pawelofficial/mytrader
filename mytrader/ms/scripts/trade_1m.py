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


d=ms.data.Data()

df = d.get_binance_candles("BTCUSDT", interval="1h", limit=100000)
exit(1)
d.recalculate_all()
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
    d.get_binance_candles('BTCUSDT',interval='5m',limit=600)
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
    if count > 5 or is_starting:
        logger.info('optimizing')
        PARAM=optimize()
        count=0
        is_starting=False
    
    delta=d.get_time_to_candle_close(interval='5m')
    if delta > 5 :
        logger.info(f'sleeping {delta-5.1}')
        print(f'sleeping {delta-5.1}')
        sleep_with_countdown(delta-5.1)
        
    else:
        count+=1
        logger.info('time to trade ! ')
        last_candle=d.get_last_candle(interval='5m')
        logger.info(f'last candle {last_candle}')

        d.delsert_df(last_candle)
        d.recalculate_all()
        sig=s.strategy(params=[PARAM],save=True)
        bl=sig.iloc[-1]       
        logger.info(f'signal {bl}, last_order {tb.last_order}')
        if bl==1:
            if tb.last_order['side']=='SELL':
                logger.info('----> buying')
                o,amos=tb.buy('bitek', 20)
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
            else:
                logger.info('----> no position to buy')
        if bl==0:
            
            if tb.last_order['side']=='BUY':
                logger.info('----> selling')
                o,amos=tb.sell('bitek',-1)
                logger.info(f'order {o}')
                logger.info(f'amos {amos}')
            else:
                logger.info('----> no position to sell')    
        time.sleep(6)
#    
#    
#    
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connection.py", line 199, in _new_conn
#    sock = connection.create_connection(
#  File "C:\gh\this_venv\lib\site-packages\urllib3\util\connection.py", line 85, in create_connection
#    raise err
#  File "C:\gh\this_venv\lib\site-packages\urllib3\util\connection.py", line 73, in create_connection
#    sock.connect(sa)
#TimeoutError: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond
#
#The above exception was the direct cause of the following exception:
#
#Traceback (most recent call last):
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connectionpool.py", line 789, in urlopen
#    response = self._make_request(
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connectionpool.py", line 490, in _make_request
#    raise new_e
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connectionpool.py", line 466, in _make_request
#    self._validate_conn(conn)
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connectionpool.py", line 1095, in _validate_conn
#    conn.connect()
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connection.py", line 693, in connect
#    self.sock = sock = self._new_conn()
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connection.py", line 214, in _new_conn
#    raise NewConnectionError(
#urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x00000220B2DAE370>: Failed to establish a new connection: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a 
#period of time, or established connection failed because connected host has failed to respond
#
#The above exception was the direct cause of the following exception:
#
#Traceback (most recent call last):
#  File "C:\gh\this_venv\lib\site-packages\requests\adapters.py", line 667, in send
#    resp = conn.urlopen(
#  File "C:\gh\this_venv\lib\site-packages\urllib3\connectionpool.py", line 843, in urlopen
#    retries = retries.increment(
#  File "C:\gh\this_venv\lib\site-packages\urllib3\util\retry.py", line 519, in increment
#    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
#urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.binance.com', port=443): Max retries exceeded with url: /api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x00000220B2DAE370>: Failed to establish a new connection: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond'))
#
#During handling of the above exception, another exception occurred:
#
#Traceback (most recent call last):
#  File "C:\gh\mytrader\mytrader\ms\scripts\trade_5m.py", line 38, in <module>
#    last_candle=d.get_last_candle()
#  File "C:\gh\mytrader\mytrader\ms\data.py", line 89, in get_last_candle
#    df=self.get_binance_candles("BTCUSDT", interval="5m", limit=1,save=False)
#  File "C:\gh\mytrader\mytrader\ms\data.py", line 99, in get_binance_candles
#    response = requests.get(url, params=params)
#  File "C:\gh\this_venv\lib\site-packages\requests\api.py", line 73, in get
#    return request("get", url, params=params, **kwargs)
#  File "C:\gh\this_venv\lib\site-packages\requests\api.py", line 59, in request
#    return session.request(method=method, url=url, **kwargs)
#  File "C:\gh\this_venv\lib\site-packages\requests\sessions.py", line 589, in request
#    resp = self.send(prep, **send_kwargs)
#  File "C:\gh\this_venv\lib\site-packages\requests\sessions.py", line 703, in send
#    r = adapter.send(request, **kwargs)
#  File "C:\gh\this_venv\lib\site-packages\requests\adapters.py", line 700, in send
#    raise ConnectionError(e, request=request)
#requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.binance.com', port=443): Max retries exceeded with url: /api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 
#0x00000220B2DAE370>: Failed to establish a new connection: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond'))
