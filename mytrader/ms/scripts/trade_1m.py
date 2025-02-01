import ms 
import requests 
import pandas as pd 

import requests

import requests

d=ms.data.Data()
# Example usage: fetch and print the last candle for BTC/USDT
historical_df = d.get_binance_candles("BTCUSDT", interval="1d", limit=1000)


