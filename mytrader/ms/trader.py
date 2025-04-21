from .data import Data 
from .strategy import Strategy
from .trade_binance import Trade
import time 
from .utils import setup_logger
import datetime
import json 
import pandas as pd 
class Trader:
    def __init__(self):
        self.interval='5m'
        self.nrows=300
        self.params=0
        self.trade_delta=5 # time to execute 
        self.previous_order={'side':None,'succesfull':None}
        self.logger=setup_logger('trader')
        self.lambda_strategy = lambda d: Strategy(d)
        self.strategy= Strategy(None)
        self.data=Data()
        self.binance=Trade()
        self.signal_dic={'portfolio':'', 'comment':'---','datetime':'','signal':'','action':'','amos':'','order':'', 'candle':'','last_order':''}
        self.signal_df=pd.DataFrame(columns=self.signal_dic.keys())
        self.signal_dics=[]
    def sleep_with_countdown(self,total_seconds):
        total_seconds = int(total_seconds)
        for remaining in range(total_seconds, 0, -1):
            self.logger.info(f"\rSleeping... {remaining} sec remaining")
            time.sleep(1)

        self.logger.info("\rDone sleeping!")
        
    def optimize(self):
        self.data.get_binance_candles('BTCUSDT',interval=self.interval,limit=self.nrows)
        self.data.recalculate_all()
        self.strategy.data=self.data 
        _=self.strategy.optimize()
        param=_['params']
        self.logger.info(f'optimized params {_}')
        sig=self.strategy.strategy(params=[param],save=True)
        bl=sig.iloc[-1]    
        self.signal_dic['signal']=bl

        
    def check_signal(self):
        last_candle=self.data.get_last_candle(self.interval)
        self.data.delsert_df(last_candle)
        self.data.recalculate_all()
        self.optimize()


    def trade(self):
        # sell everything 
        self.binance.sell('bitek',-1)
        portfolio=self.binance.check_portfolio()
        
        
        order={}
        action=None
        amos=None
        # run loop 
        while True:
            action='no action'
            portfolio=self.binance.check_portfolio()
            self.signal_dic['portfolio']=portfolio
            
            self.signal_dic['datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            delta=self.data.get_time_to_candle_close(interval=self.interval)
            self.logger.info(f"delta: {delta}")
            if False:
                pass
            if delta > self.trade_delta:
                print('sleeping for ',delta-self.trade_delta-0.1)
                self.logger.info(f'sleeping for {delta-self.trade_delta-0.1}')
                self.sleep_with_countdown(delta-self.trade_delta+0.1)
            else:                
                self.logger.info(f"checking signal .... ")
                self.check_signal()
                signal=self.signal_dic['signal']
                self.logger.info(f"signal_dic {self.signal_dic}")
                
                last_trade=self.binance.last_order['side']
                self.logger.info(f"last_trade {last_trade}")
                self.logger.info(f"signal {signal}")
                

                if signal==1:
                    self.signal_dic['datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if last_trade=='SELL' or last_trade is None:
                        action='buy'
                        self.logger.info('BUYING')
                        order,amos=self.binance.buy('bitek', 40)
                        self.binance.last_order['side']='BUY'
 
                if signal ==0:
                    if last_trade=='BUY':
                        action='sell'
                        self.signal_dic['datetime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.logger.info('SELLING')
                        order,amos=self.binance.sell('bitek', -1)
                        self.binance.sell('bitek',-1)
                        
                status=order.get('status')
                self.signal_dic['comment']=status
                self.signal_dic['amos']=amos
                self.signal_dic['action']=action
                self.signal_dic['candle']=str(self.data.get_last_candle(self.interval).to_dict())
                self.signal_dic['last_order']=order
                self.signal_df.loc[len(self.signal_df)]=self.signal_dic.copy()
                self.sleep_with_countdown(self.trade_delta)
                # save signal dics 
                self.signal_df.to_csv('signal.csv',index=False,sep='|')
                order={}

        
        
