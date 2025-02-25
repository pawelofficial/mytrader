# cd  C:\gh\mytrader\mytrader
# python -m ms.scripts.backtest
import ms 

d=ms.data.Data()



d.df=d.get_binance_candles('BTCUSDT',interval='1h',limit=600)


d.recalculate_all()
s=ms.strategy.Strategy(d)
dic=s.optimize()
sig =s.strategy(params=[dic['params']],save=True)  # -4.24927704
ser=d.df['sig_raw']

#
profit=s.calculate_profit_scalp(sig,price_ser=d.df['close'],save=True)
print(profit)

p=ms.Plotter(d.df)

p.candleplot(interval=d.data_interval,asset=d.fname)