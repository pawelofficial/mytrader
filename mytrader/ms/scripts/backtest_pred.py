# cd  C:\gh\mytrader\mytrader
# python -m ms.scripts.backtest

# backtest on n, test on N data 
import ms 

d=ms.data.Data()




N=1000
n=800
df=d.get_binance_candles('BTCUSDT',interval='15m',limit=N)
d.df=df[:n].copy()
test_df=df[-(N-n):].copy()


d.recalculate_all()
s=ms.strategy.Strategy(d)
dic=s.optimize()
sig =s.strategy(params=[dic['params']],save=True)  # -4.24927704
ser=d.df['sig_raw']

d.df=test_df
d.recalculate_all()
s=ms.strategy.Strategy(d)
sig =s.strategy(params=[dic['params']],save=True)  # -4.24927704
ser=d.df['sig_raw']


#
profit=s.calculate_profit_scalp(sig,price_ser=d.df['close'],save=True)
print(profit)

p=ms.Plotter(d.df)

p.candleplot(interval=d.data_interval,asset=d.fname)