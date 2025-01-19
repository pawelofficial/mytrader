

import ms
import ms.data 
import ms.strategy
import ms.trade_binance 
import pandas as pd 
from matplotlib import pyplot as plt
from tabulate import tabulate
import random 
#d=ms.Downloader()
#d.download_historical_data()

tb=ms.trade_binance.Trade()
btc=tb.get_balance('BTC')
usdt=tb.get_balance('USDT')
print(usdt,btc)

#o,amos=tb.buy('bitek', 20)
#print(tb.last_order)
#print(amos)
#qty=tb.get_balance('BTC')
o,amos=tb.sell('bitek',-1)
print(tb.last_order)
#print(amos)
exit(1)





def plot_candlestick(df=None
                     ,start_date='2025-01-01'
                     ,end_date='2025-01-15'
                    ,datetime_colunm='datetime'
                     ):
    if df is None : 
        d=ms.data.Data()
        df=d.df
    # filter df based on datetime columns    
    if start_date is not None or end_date is not None:
        df=df[df[datetime_colunm]>=start_date] 
        df=df[df[datetime_colunm]<=end_date]
    
    ## make random signal 
    #df['signal']=0
    #df['signal'] = df['signal'].apply(lambda x: 1 if random.random() > 0.9 else -1)
    #print(df)
    p=ms.plotter.Plotter(df)
    p.candleplot()

d=ms.data.Data()
##1. download data 
#d._download_historical_data(interval='1h')
d.recalculate_all()

##2. normalize data 
d.normalize()

##3. filter data 
d.filter(start_date='2025-01-01',end_date='2025-01-14')

##4. run a strategy
s=ms.strategy.Strategy(d)

# run a strategy 
if 1:
    sig =s.strategy(params=[-3.50914227])  # -5.674305 -2.94403494
    profit2=s.calculate_profit_scalp(sig,save=True)
    print(profit2)

    
    map={'NONE':0,'LONG':1,'SHORT':-1,'' : 0}
    d.df['signal']=d.df['position'].apply(lambda x: map[x])
    print(d.df)
    
    plot_candlestick(d.df)
#    exit(1)

# optimize 

#profit2=s.calculate_profit(sig,save=True)

cols=['datetime','close','position','total_profit','shares','position_size','capital']
N=100
msk=d.df['position']!='NONE'
print(tabulate(s.data.df[msk][cols].iloc[:N] , headers='keys', tablefmt='pretty'))
exit(1)

#print(profit,profit2)
s.optimize()
exit(1)
#s.optimize()

# make df from price and ema_signal_close

#d.download_historical_data()
if 1:
    p=ms.plotter.Plotter(d.df)

    p.simplest_scatter_plot(d,show=False
                            ,ema_cols=['ema_10','ema_20']
                            ,signal_cols=['signal']
                            ,subplot=(True,'total_profit')
                            )
    print('ok')