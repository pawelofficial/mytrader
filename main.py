

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
s.ema_strategy(ema1='ema_10',ema2='ema_20',sign='<')
profit=s.calculate_profit_all_in()
print(profit)
# print d attributes 



#d.download_historical_data()

p=ms.plotter.Plotter(d.df)

p.simplest_scatter_plot(d,show=False
                        ,ema_cols=['ema_10','ema_20']
                        ,signal_col='ema_signal'
                        ,subplot=(True,'total_profit_ema_signal')
                        )
print('ok')