# cd  C:\gh\mytrader\mytrader
# python -m ms.scripts.script1
import ms 

d=ms.data.Data()

d._download_historical_data(interval='1h'
                            ,start_ts='week_ago'
                            ,end_ts='today')

d.recalculate_all()
s=ms.strategy.Strategy(d)
sig =s.strategy(params=[-5.06580535],save=True)  # -4.24927704
#
profit=s.calculate_profit_scalp(sig,price_ser=d.df['close'],save=True)
print(profit)

p=ms.Plotter(d.df)
p.candleplot()