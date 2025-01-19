import ms
import ms.data 
import ms.strategy
import ms.trade_binance
import pandas as pd 
import time 

 



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
    bl=c.check_clock()
    if not bl:
        print('waiting for clock')
        time.sleep(45)
        continue
    else:
        print('lets go!')
        d._download_historical_data(interval='5m'
                                    ,start_ts=pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()+ pd.DateOffset(minutes=-5)))   
                                    ,end_ts=pd.to_datetime(pd.Timestamp.now().normalize() + pd.DateOffset(days=1))  # tomorrow
                                    )

        d.recalculate_all()
        s=ms.strategy.Strategy(d)
        sig =s.strategy(params=[-5.06580535])

        signal=sig.iloc[-1]

        last_trade=tb.last_order['side']
        if signal ==1:
            if last_trade=='SELL':
                print('buying')
                o,amos=tb.buy('bitek', 20)
                print(tb.last_order)
        elif signal !=1 :
            if last_trade=='BUY':
                print('selling')
                o,amos=tb.sell('bitek',-1)
                print(tb.last_order)
        time.sleep(45)
