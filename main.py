

import ms
import ms.data 
import ms.strategy
import pandas as pd 
from matplotlib import pyplot as plt

#d=ms.Downloader()
#d.download_historical_data()

d=ms.data.Data()

#d._download_historical_data()
print(d.columns)
d.recalculate_all()

d.normalize()
# filter df to datetime < 1990
# cast datetime to datetime 
d.df['datetime'] = pd.to_datetime(d.df['datetime'], utc=True)
# Convert the comparison date to the same timezone
comparison_date = pd.to_datetime('1995-01-01').tz_localize('UTC')
# Filter the DataFrame
#d.df = d.df[d.df['datetime'] < comparison_date]

s=ms.strategy.Strategy(d)
s.ema_strategy(ema1='ema_10',ema2='ema_20',sign='<')
sig =s.strategy(params=[-2.94403494])
d.df['signal']=sig
#profit=s.calculate_profit_all_in(signal_column='sig')
profit2=s.calculate_profit(sig,save=True)
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