

import ms
import ms.data 


#d=ms.Downloader()
#d.download_historical_data()

d=ms.data.Data()
#d.download_historical_data()
print(d.columns)
d.calculate_emas()
print(d.columns)
#d.download_historical_data()

p=ms.plotter.Plotter()