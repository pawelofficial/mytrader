

import ms
import ms.data 


#d=ms.Downloader()
#d.download_historical_data()

d=ms.data.Data()
d.download_historical_data()

p=ms.plotter.Plotter()