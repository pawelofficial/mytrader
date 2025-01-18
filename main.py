

import ms
import ms.data 
import ms.strategy
import pandas as pd 
from matplotlib import pyplot as plt
from tabulate import tabulate
import random 
#d=ms.Downloader()
#d.download_historical_data()

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
#d._download_historical_data(interval='1h')
d.recalculate_all()
d.normalize()
#d.filter(start_date='2024-01-01',end_date='2024-01-14')


s=ms.strategy.Strategy(d)
s.ema_strategy(ema1='ema_10',ema2='ema_20',sign='<')
sig =s.strategy(params=[-3.50914227])  # -5.674305 -2.94403494
profit2=s.calculate_profit_scalp(sig,save=True)
#profit2=s.calculate_profit(sig,save=True)
d.df['signal']=sig
map={'NONE':0,'LONG':1,'SHORT':-1}
d.df['signal']=d.df['position'].apply(lambda x: map[x])
print(d.df)
plot_candlestick(d.df)
exit(1)


profit2=s.calculate_profit_scalp(sig,save=True)
print(profit2)
#profit2=s.calculate_profit(sig,save=True)

cols=['datetime','close','position','total_profit','shares','position_size','capital']
N=100
msk=d.df['position']!='NONE'
print(tabulate(s.data.df[msk][cols].iloc[:N] , headers='keys', tablefmt='pretty'))


#print(profit,profit2)
s.optimize()
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