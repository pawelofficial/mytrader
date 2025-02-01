from ms.data import Data
import unittest
import pandas as pd 

# python -m unittest tests.test_data
class TestData(unittest.TestCase):
    def setUp(self):
        self.data = Data()
        self.test_df =Data()._download_historical_data(ticker='BTC', start_ts='2024-12-01', end_ts='today', interval='1d')
        
    def test_read_data(self):
        """Test if data is read correctly"""
        
        self.assertIsInstance(self.data.df, pd.DataFrame)
        self.assertIn('datetime', self.data.df.columns)
        self.assertFalse(self.data.df.isnull().values.any())
    
    def test__download_historical_data(self):
        """Test if data is downloaded correctly"""
        self.data._download_historical_data(ticker='BTC', start_ts='2024-12-01', end_ts='today', interval='1d')
        self.assertIsInstance(self.data.df, pd.DataFrame)
        self.assertIn('datetime', self.data.df.columns)
        self.assertFalse(self.data.df.isnull().values.any())
        
        yesterday=pd.Timestamp.now().normalize()-pd.DateOffset(days=1)
        self.data._download_historical_data(ticker='BTC', start_ts=yesterday, end_ts='today', interval='5m')
        self.assertIsInstance(self.data.df, pd.DataFrame)
        self.assertIn('datetime', self.data.df.columns)
        self.assertFalse(self.data.df.isnull().values.any())
        