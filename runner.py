import ms
import ms.data 
import ms.strategy
import ms.trade_binance
import pandas as pd 
import time 

from ms.utils import setup_logger
logger=setup_logger('runner')

 



class clock():
    def __init__(self):
        self.data=ms.data.Data()
        self.bl=False

    def check_clock(self):
        data_1m=self.data._download_historical_data(interval='1m'
                                    ,start_ts=pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()+ pd.DateOffset(minutes=-5)))   
                                    ,end_ts=pd.to_datetime(pd.Timestamp.now().normalize() + pd.DateOffset(days=1))  # tomorrow
                                    )

        data_5m=self.data._download_historical_data(interval='5m'
                                    ,start_ts=pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()+ pd.DateOffset(minutes=-5)))   
                                    ,end_ts=pd.to_datetime(pd.Timestamp.now().normalize() + pd.DateOffset(days=1))  # tomorrow
                                    )



        this_candle_end=data_5m.iloc[-1]['datetime']
        last_candle_end=data_1m.iloc[-1]['datetime']
        bl=this_candle_end==last_candle_end
        self.bl=bl
        return bl



c=clock()
tb=ms.trade_binance.Trade()
o,amos=tb.sell('bitek',-1)
tb=ms.trade_binance.Trade()
btc=tb.get_balance('BTC')
usdt=tb.get_balance('USDT')

# 5.23e-06 21.90930532
print(btc,usdt)


d=ms.data.Data()

while True:
    try:
        bl=c.check_clock()
        logger.info(f'retrying clock')
    except Exception as e:
        time.eleep(61)
        bl=c.check_clock()
    
    if not bl:
        logger.info('waiting for clock')
        time.sleep(45)
        continue
    else:
        
        logger.info('lets go!')
        try:
            d._download_historical_data(interval='5m'
                                        ,start_ts=pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()+ pd.DateOffset(days=-1)))   
                                        ,end_ts=pd.to_datetime(pd.Timestamp.now().normalize() + pd.DateOffset(days=1))  # tomorrow
                                        )
        except Exception as e:
            logger.error(f'retrying download')
            time.sleep(61)
            d._download_historical_data(interval='5m'
                                        ,start_ts=pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()+ pd.DateOffset(days=-1)))   
                                        ,end_ts=pd.to_datetime(pd.Timestamp.now().normalize() + pd.DateOffset(days=1))  # tomorrow
                                        )
            

        d.recalculate_all()
        s=ms.strategy.Strategy(d)
        sig =s.strategy(params=[-5.06580535])

        signal=sig.iloc[-1]

        last_trade=tb.last_order['side']
        if signal ==1:
            logger.info('signal 1 ')
            if last_trade=='SELL' or last_trade==None:
                logger.info('buying')
                o,amos=tb.buy('bitek', 20)
                logger.info(tb.last_order)
                
        elif signal !=1 :
            logger.info('signal -1 ')
            if last_trade=='BUY' or last_trade==None:
                logger.info('selling')
                o,amos=tb.sell('bitek',-1)
                logger.info(tb.last_order)
        time.sleep(45)
