import os
import pandas as pd
import yfinance as yf
from ms.utils import setup_logger

def update_columns_after(func):
    """Update DataFrame columns as attributes after function execution."""
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._set_columns_as_attributes()
        return result
    return wrapper

class Data:
    def __init__(self):
        self.this_path = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.this_path, 'data')
        self.logger = setup_logger('data')
        self.base_columns = ['open', 'close', 'low', 'high']
        self.tickers_map = {'SPX': '^GSPC', 'BTC': 'BTC-USD'}
        self.__read_data()

    def __read_data(self, fname='BTC.csv'):
        self.logger.info(f'Reading data from {fname}')
        file_path = os.path.join(self.data_path, fname)
        self.df = pd.read_csv(file_path)
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        if self.df.isnull().values.any():
            raise ValueError("Data contains NaN values")

    def filter(self, start_date=None, end_date=None):
        start_date = self.df['datetime'].min() if start_date == 'start' else pd.to_datetime(start_date, utc=True)
        end_date = self.df['datetime'].max() if end_date == 'today' else pd.to_datetime(end_date, utc=True)
        self.df = self.df[(self.df['datetime'] >= start_date) & (self.df['datetime'] <= end_date)]

    def _download_historical_data(self, ticker='BTC', start_ts='2024-12-01', end_ts='today', interval='1d', save=True):
        self.logger.info(f'Downloading {ticker} data from {start_ts} to {end_ts} at {interval} interval')
        if end_ts == 'today':
            end_ts = pd.Timestamp.now().normalize()
        start_ts, end_ts = pd.to_datetime(start_ts), pd.to_datetime(end_ts)
        if start_ts is None or end_ts is None:
            raise ValueError("Timestamps cannot be None")
        data = yf.download(self.tickers_map[ticker], start=start_ts, end=end_ts, interval=interval)
        self.logger.info(f'Downloaded data shape: {data.shape}')
        data.columns = data.columns.droplevel('Ticker')
        data.reset_index(inplace=True)
        data.columns = [col.lower() for col in data.columns]
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
        return data

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
                raise ValueError(f"NaN values found in sma_{sma}")

    @update_columns_after
    def calculate_ema_derivatives(self, emas=[5, 10, 20, 50, 100], smooth=5):
        for ema in emas:
            self.df[f'ema_{ema}_der'] = (
                self.df[f'ema_{ema}']
                .diff()
                .rolling(window=smooth, center=True, min_periods=1)
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
            raise ValueError("NaN values found in base columns")
        self.recalculate_all()

if __name__ == '__main__':
    pass
