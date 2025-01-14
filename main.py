

import ms
import ms.data 


#d=ms.Downloader()
#d.download_historical_data()

d=ms.data.Data()
#d._download_historical_data()
print(d.columns)
d.recalculate_all()
d.normalize()

#d.download_historical_data()

p=ms.plotter.Plotter()
p.simplest_scatter_plot(d,show=False,ema_cols=['ema_5','ema_10','ema_20','ema_50','ema_100'])