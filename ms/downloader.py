import logging
import re 
import os 
import pandas as pd 
from  pytickersymbols import PyTickerSymbols
import yfinance as yf
if __name__=='__main__':
    from utils import setup_logger
else:
    from .utils import setup_logger


class Downloader:
    def __init__(self):
        self.this_path=os.path.dirname(os.path.abspath(__file__))
        self.data_path=os.path.join(self.this_path,'data')
        self.logger=setup_logger('downloader')
        self.logger.info('Data object created')
        self.tickers_map={'SPX':'^GSPC'}    
    
    
    # downloads historical data 
    def download_historical_data(self
                                 ,ticker='SPX'
                                 ,start_ts = '1990-01-01' # yyyy-mm-dd 
                                 ,end_ts   = 'today' 
                                 ,interval = '1d'                
                                 ,save=True      
                                 ):
        self.logger.info(f'Downloading data for {ticker} from {start_ts} to {end_ts} with interval {interval}')
        
        if end_ts=='today':
            end_ts= pd.to_datetime(pd.to_datetime(pd.Timestamp.now().normalize()))    
        
        start_ts = pd.to_datetime(start_ts) if start_ts is not None else None
        end_ts = pd.to_datetime(end_ts) if end_ts is not None else None
        
        if start_ts is None or end_ts is None:
            raise('ts cant be none ')

        self.logger.info('trying to download ... ')
        data = yf.download(self.tickers_map[ticker], start=start_ts, end=end_ts, interval=interval)
        self.logger.info(f'downloaded {data.shape} data ')
        
        self.logger.info('changing data structure')
        data.columns = data.columns.droplevel('Ticker')  # Drop the 'Ticker' level
        data.reset_index(inplace=True)
        data.columns=[col.lower() for col in data.columns]

        
        if 'datetime' in data.columns:
            data['unixtime']=data['datetime'].astype('int64') / 10**9
            data['datetime']=pd.to_datetime(data['datetime'])
        
        elif 'date' in data.columns:
            data['unixtime']=data['date'].astype('int64') / 10**9
            data.rename(columns={'date':'datetime'},inplace=True)
            # cast to datetime 2024-12-31 20:30:00+00:00
            data['datetime']=pd.to_datetime(data['datetime']).dt.tz_localize('UTC')
        else:
            print('no date column in data ')
            print(data.columns)
            exit(1)

        self.logger.info('changing structure ok ')
        if save:
            self.logger.info('saving data')
            data.to_csv(os.path.join(self.data_path,f'{ticker}.csv'))
        else:
            self.logger.info('not saving data')

        return data 

        
if __name__ == '__main__':
    d=Downloader()
    stocks=d.get_nasdaq_symbols()
    d.download_historical_data()
