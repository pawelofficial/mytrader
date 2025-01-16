

import ms
import ms.data 
import ms.strategy

#d=ms.Downloader()
#d.download_historical_data()

d=ms.data.Data()
#d._download_historical_data()
print(d.columns)
d.recalculate_all()
d.normalize()

s=ms.strategy.Strategy(d)
s.ema_strategy()
profit=s.calculate_profit()
print(profit)
# print d attributes 



#d.download_historical_data()

p=ms.plotter.Plotter(d.df)
p.simplest_scatter_plot(d,show=False
                        ,ema_cols=['ema_5','ema_10','ema_20','ema_50','ema_100']
                        ,signal_col='ema_signal'
                        ,subplot=(True,'total_profit_ema_signal')
                        )
print('ok')