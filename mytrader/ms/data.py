import os
import pandas as pd
import yfinance as yf
import datetime
import requests
from ms.utils import setup_logger
import numpy as np 

def update_columns_after(func):
    """Update DataFrame columns as attributes after function execution."""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._set_columns_as_attributes()
        return result
    return wrapper

class Data:
    def __init__(self, fname='BTC.csv'):
        self.this_path = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.this_path, 'data')
        self.logger = setup_logger('data')
        self.base_columns = ['open', 'close', 'low', 'high','volume']
        self.tickers_map = {'SPX': '^GSPC', 'BTC': 'BTC-USD','BTCUSDT':'BTC'}
        self.fname = fname
        self.last_candle=None
        self.__read_data()
        self.data_interval=self.calculate_data_interval()

    def calculate_data_interval(self):
        # get the difference between the first and second candle
        delta = self.df['datetime'].diff().iloc[1].seconds
        map={'60':'1m','300':'5m','900':'15m','1800':'30m','3600':'1h','14400':'4h','86400':'1d'}
        try:
            return map[str(delta)]
        except:
            raise ValueError(f'interval {delta} not found')    

    def delsert_df(self, row: pd.Series):
        # Ensure row has all columns, fill missing with NaN
        row = row.reindex(self.df.columns, fill_value=np.nan)
        last_candle = self.df.iloc[-1]
        if last_candle['close_time'] == row['close_time']:
            # Update the last row
            self.df.iloc[-1] = row
            return self.df
        
        self.df.loc[len(self.df)]=row
        # drop first row 
        self.df=self.df.iloc[1:]
        return self.df

    def __read_data(self):
        self.logger.info(f'Reading data from {self.fname}')
        file_path = os.path.join(self.data_path, self.fname)
        # check if file exists 
        if not os.path.exists(file_path):
            print('file does not exist - download it ')
            return 
            #raise FileNotFoundError(f"File {file_path} not found")
        
        self.df = pd.read_csv(file_path)
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        if self.df.isnull().values.any():
            raise ValueError("Data contains NaN values")

    def __parse_date_words(self, word):
        if word not in ['start', 'yesterday', 'week_ago']:
            return pd.to_datetime(word, utc=True)
        if word == 'yesterday':
            return pd.Timestamp.now().normalize()-pd.DateOffset(days=1)
        if word == 'week_ago':
            return pd.Timestamp.now().normalize()-pd.DateOffset(days=7)
        if word =='month_ago':
            return pd.Timestamp.now().normalize()-pd.DateOffset(months=1)
        if word == 'start':
            return self.df['datetime'].min()
        if word == 'today':
            return pd.Timestamp.now().normalize()
        if word == 'end':
            return pd.Timestamp.now().normalize()
        
        return pd.to_datetime(word, utc=True)

    def filter(self
               , start_date=None # start / yesterday / yyyy-mm-dd
               , end_date=None): # today / yyyy-mm-dd
        start_date = self.__parse_date_words(start_date)
        end_date = self.__parse_date_words(end_date)
        
        self.df = self.df[(self.df['datetime'] >= start_date) & (self.df['datetime'] <= end_date)]

    def map_interval(self,interval):
        dic={'1m':0,'5m':5,'15m':15,'30m':30,'1h':60,'4h':240,'1d':1440}
        return dic[interval]

    def get_last_candle(self,interval='1m'):
        df=self.get_binance_candles("BTCUSDT", interval=interval, limit=1,save=False)
        return df.iloc[-1]

    def to_milliseconds(self,date_str):
        """Convert a date string (YYYY-MM-DD) to Binance timestamp (milliseconds)."""
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Use datetime.datetime
        return int(dt.timestamp() * 1000)
    
    def to_datetime(self,unixtimestamp):
        return pd.to_datetime(unixtimestamp,unit='ms')
    

    def get_many_binance_candles(self,symbol,interval,startTime,endTime,save=True):
        startime=self.to_milliseconds(startTime)
        endtime=self.to_milliseconds(endTime)
        filenames=[]
        while True:
            df=self.get_binance_candles(symbol, interval=interval, limit=500,startTime=startime,endTime=None,save=False)
            start=str(self.to_datetime(df['unixtimestamp'].iloc[0])).replace(':','_').replace(' ','_')
            end=str(self.to_datetime(df['unixtimestamp'].iloc[-1])).replace(':','_').replace(' ','_')
            filename = os.path.join(self.data_path, f'{self.tickers_map[symbol]}_{start}_{end}.csv')
            df.to_csv(filename)
            startime=df['unixtimestamp'].iloc[-1]+1
            filenames.append(filename)
            if startime > endtime:
                break
            
        master_df=pd.concat([pd.read_csv(filename) for filename in filenames])
        master_df.to_csv(os.path.join(self.data_path, f'{self.tickers_map[symbol]}_{startTime}_{endTime}.csv'))
        
        # go through files to check if there are any missing candles
        for filename in filenames:
            df=pd.read_csv(filename)
            if len(df) != 500 and filename !=filenames[-1]: # last filename wont have 500 candles
                print(f'file {filename} has {len(df)} candles')
                print(df)
                raise ValueError('missing candles')
        
        
        return master_df

    def get_binance_candles(self,symbol, interval="1m"
                            , limit=1000     # fetches this number of candles
                            , startTime=None # unixtimestamp 
                            , endTime=None  # unixtimestamp 
                            ,save=True
                            ):
        
        print('downloading the data ! ')
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        response = requests.get(url, params=params)
        response.raise_for_status()
        candles = response.json()

        # Format each candle as a list
        formatted_candles= [
            [
                candle[0],    # Open time
                candle[1],    # Open price
                candle[2],    # High price
                candle[3],    # Low price
                candle[4],    # latest price / close price 
                candle[5],    # Volume
                candle[6],    # Close time
                candle[7],    # Quote asset volume
                candle[8],    # Number of trades
                candle[9],    # Taker buy base asset volume
                candle[10],   # Taker buy quote asset volume
                candle[11]    # Ignore
            ]
            for candle in candles
        ]


        dic={'unixtimestamp':formatted_candles[0][0]
             ,'close_time':formatted_candles[0][6]
             ,'datetime':pd.to_datetime(formatted_candles[0][0],unit='ms')
             ,'close_datetime':pd.to_datetime(formatted_candles[0][6],unit='ms')
             ,'open':formatted_candles[0][1]
             ,'close':formatted_candles[0][4]
             ,'low':formatted_candles[0][3]
             ,'high':formatted_candles[0][2]
             ,'volume':formatted_candles[0][5]
             }
        df=pd.DataFrame(columns=list(dic.keys()))
        for candle in formatted_candles:
            dic={'unixtimestamp':candle[0]
                 ,'close_time':candle[6]
                 ,'datetime':pd.to_datetime(candle[0],unit='ms')
                 ,'close_datetime':pd.to_datetime(candle[6],unit='ms')
                 ,'open':candle[1]
                 ,'close':candle[4]
                 ,'low':candle[3]
                 ,'high':candle[2]
                ,'volume':candle[5]
                 }
            df.loc[len(df)]=dic

        
        # cast base columns to float
        for col in self.base_columns:
            df[col]=df[col].astype(float)


        if save:
            print('saving the data ! ')
            self.df=df
            self.last_candle=df.iloc[-1].to_dict()
            df.to_csv(os.path.join(self.data_path, f'{self.tickers_map[symbol]}.csv'))

        return df


    def _download_historical_data(self, ticker='BTC'
                                  , start_ts='2024-12-01'
                                  , end_ts='today'
                                  , interval='1d'
                                  , save=True):
        self.logger.info(f'Downloading {ticker} data from {start_ts} to {end_ts} at {interval} interval')
        

        start_ts = self.__parse_date_words(start_ts)
        end_ts = self.__parse_date_words(end_ts)

        data = yf.download(self.tickers_map[ticker], start=start_ts, end=end_ts, interval=interval,progress=False)

        self.logger.info(f'Downloaded data shape: {data.shape}')
        data.columns = data.columns.droplevel('Ticker')
        data.reset_index(inplace=True)
        data.columns = [col.lower() for col in data.columns]
        
        # depending on download interval, datetime column may not be present
        if 'datetime' in data.columns:
            data['unixtime'] = data['datetime'].astype('int64') // 10**9
            data['datetime'] = pd.to_datetime(data['datetime'])
        elif 'date' in data.columns:
            data['unixtime'] = data['date'].astype('int64') // 10**9
            data.rename(columns={'date': 'datetime'}, inplace=True)
            data['datetime'] = pd.to_datetime(data['datetime']).dt.tz_localize('UTC')
        else:
            self.logger.error("No date column found in data")
            raise ValueError("No date column in downloaded data")

        if save:
            data.index.name = 'index'
            data.to_csv(os.path.join(self.data_path, f'{ticker}.csv'))
        self.df=data

        return data

    def get_time_to_candle_close(self,interval='1m',symbol='BTCUSDT'):
        # get last candle 
        last_candle=self.get_binance_candles(symbol, interval=interval, limit=1,save=False).iloc[-1].to_dict()
        unixtime_now=(datetime.datetime.now() - datetime.timedelta(hours=0)).timestamp() * 1000
        delta=(last_candle['close_time']-unixtime_now) /1000
        return delta 


    @property
    def columns(self):
        if self.df is not None:
            self._set_columns_as_attributes()
            return self.df.columns
        raise ValueError("No DataFrame loaded")

    def _set_columns_as_attributes(self):
        for col in self.df.columns:
            setattr(self, col, self.df[col])

    @update_columns_after
    def calculate_emas(self, emas=[5, 10, 20, 50, 100]):
        for ema in emas:
            self.df[f'ema_{ema}'] = (
                self.df['close']
                .ewm(span=ema, adjust=False)
                .mean()
                .fillna(method='bfill')
            )
            if self.df[f'ema_{ema}'].isnull().any():
                print(self.df)
                raise ValueError(f"NaN values found in ema_{ema}")

    @update_columns_after
    def calculate_smas(self, smas=[5, 10, 20, 50, 100]):
        for sma in smas:
            self.df[f'sma_{sma}'] = (
                self.df['close']
                .rolling(window=sma)
                .mean()
                .fillna(method='bfill')
            )
            if self.df[f'sma_{sma}'].isnull().any():
                print(self.df[f'sma_{sma}'])
                raise ValueError(f"NaN values found in sma_{sma}")

    @update_columns_after
    def calculate_ema_derivatives(self, emas=[5, 10, 20, 50, 100], smooth=5):
        for ema in emas:
            self.df[f'ema_{ema}_der'] = (
                self.df[f'ema_{ema}']
                .diff()
                .rolling(window=smooth, center=True, min_periods=1) # center True introduces lookahead bias 
                .mean()
                .fillna(method='bfill')
                .fillna(method='ffill')
            )
            if self.df[f'ema_{ema}_der'].isnull().any():
                raise ValueError(f"NaN values found in ema_{ema}_der")

    @update_columns_after
    def calculate_rsi(self, rsi_period=14):
        delta = self.df['close'].diff()
        gain = delta.clip(lower=0).ewm(span=rsi_period).mean()
        loss = (-delta.clip(upper=0)).ewm(span=rsi_period).mean()
        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))

    def calculate_macd(self, short=12, long=26, signal=9):
        self.df['short_ema'] = self.df['close'].ewm(span=short, adjust=False).mean()
        self.df['long_ema'] = self.df['close'].ewm(span=long, adjust=False).mean()
        self.df['macd'] = self.df['short_ema'] - self.df['long_ema']
        self.df['macd_signal'] = self.df['macd'].ewm(span=signal, adjust=False).mean()
        self.df['macd_histogram'] = self.df['macd'] - self.df['macd_signal']
        self._set_columns_as_attributes()

    def recalculate_all(self):
        self.calculate_emas()
        self.calculate_smas()
        self.calculate_ema_derivatives()

    def normalize(self, norm_column='sma_50'):
        self.df['real_close'] = self.df['close']
        for col in self.base_columns:
            self.df[col] -= self.df[norm_column]
        min_val = self.df[self.base_columns].min().min()
        if min_val < 0:
            for col in self.base_columns:
                self.df[col] += abs(min_val) + 1
        if self.df[self.base_columns].isnull().any().any():
            # print nan values 
            print(self.df[self.base_columns].isnull().sum())
            print(self.df)
            
            raise ValueError("NaN values found in base columns")
        self.recalculate_all()

if __name__ == '__main__':
    pass
