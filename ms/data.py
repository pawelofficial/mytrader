import os 
import pandas as pd 
from  pytickersymbols import PyTickerSymbols
import yfinance as yf


from ms.utils import setup_logger


def update_columns_after(func):
    """Decorator to update columns as attributes after the function executes."""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # Execute the original function
        self._set_columns_as_attributes()    # Update columns as attributes
        return result
    return wrapper



class Data:
    def __init__(self):
        self.this_path = os.path.dirname(os.path.abspath(__file__)) 
        self.data_path = os.path.join(self.this_path, 'data')
        self.logger=setup_logger('data')
        self.__read_data()
        self.base_columns=['open','close','low','high']
        self.tickers_map={'SPX':'^GSPC'}    
    
    def __read_data(self,fname='SPX.csv'):
        """ reads data from data folder """
        self.logger.info(f'reading data from {fname}')
        self.df=pd.read_csv( os.path.join(self.data_path, fname))

    def _download_historical_data(self
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
            data.index.name='index'
            data.to_csv(os.path.join(self.data_path,f'{ticker}.csv'))
        else:
            self.logger.info('not saving data')

        return data 
    
    @property
    def columns(self):
        """Returns the columns of the underlying DataFrame."""
        if self.df is not None:
            self._set_columns_as_attributes()
            return self.df.columns
        else:
            raise ValueError("No DataFrame loaded to check columns.")
    
    def _set_columns_as_attributes(self):
        """Set DataFrame columns as attributes."""
        for col in self.df.columns:
            setattr(self, col, self.df[col])
    
    @update_columns_after
    def calculate_emas(self,emas=[5,10,20,50,100]):
        for ema in emas:
            self.df[f'ema_{ema}'] = self.df['close'].ewm(span=ema, adjust=False).mean()

    @update_columns_after
    def calculate_smas(self,smas=[5,10,20,50,100]):
        for sma in smas:
            self.df[f'sma_{sma}'] = self.df['close'].rolling(window=sma).mean()

    def recalculate_all(self):
        self.calculate_emas()
        self.calculate_smas()


    def normalize(self,norm_column='sma_50'):
        for col in self.base_columns:
            self.df[f'{col}']=self.df[col]-self.df[norm_column]
        self.recalculate_all()
        
    
if __name__ == '__main__':
    pass