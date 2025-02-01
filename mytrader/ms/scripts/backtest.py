# cd  C:\gh\mytrader\mytrader
# python -m ms.scripts.script1
import ms 

d=ms.data.Data()



d.get_binance_candles('BTCUSDT',interval='1h',limit=300)


d.recalculate_all()
s=ms.strategy.Strategy(d)
sig =s.strategy(params=[-5.06580535],save=True)  # -4.24927704
#
profit=s.calculate_profit_scalp(sig,price_ser=d.df['close'],save=True)
print(profit)

p=ms.Plotter(d.df)
p.candleplot()