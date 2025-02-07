import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import dotenv

import os 
dotenv.load_dotenv()

# run as script to download 
#import ms 
#d=ms.data.Data()
#d.get_many_binance_candles('BTCUSDT',interval='1h',startTime='2020-01-01',endTime='2025-01-31')
#exit(1)


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesPredictor

# Read the data
df = pd.read_csv('../data/BTC_2024-01-01_2025-01-31.csv')


NZ=100
df['rolling_z_score']=(df['close'] - df['close'].rolling(NZ).mean() ) / df['close'].rolling(NZ).std()

#plt.scatter(df['datetime'],df['rolling_z_score'])
#plt.show()
#exit(1)



# Select and rename the required columns
df = df[['datetime', 'rolling_z_score']].rename(columns={'datetime': 'timestamp', 'rolling_z_score': 'value'})

# Convert 'timestamp' column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

N = 10
train_data = df[:-N]
val_data = df[-N:]

# Add an identifier column
train_data['item_id'] = 'BTCUSDT'
val_data['item_id'] = 'BTCUSDT'

# Set the index
train_data = train_data.set_index(['item_id', 'timestamp'])
val_data = val_data.set_index(['item_id', 'timestamp'])

# Initialize the predictor
predictor = TimeSeriesPredictor(
    target='value',
    prediction_length=N,  # Forecast horizon
    freq='H'  # Assuming hourly data
)
predictor.fit(
    train_data,
    hyperparameters={
        'Chronos': {
            "model_path": "amazon/chronos-bolt-base",
            "fine_tune":True,
            "fine_tune_steps":1000,
            'token': os.getenv('HF_TOKEN'),
        }
    }
)

predictions = predictor.predict(val_data)
print(predictions)
print(val_data)

# make predictions df with mean and timestamp
pred=predictions['mean'].to_list()
vals=val_data['value'].to_list()

print(pred)
print(vals)
list1=pred
list2=vals

fig,ax=plt.subplots()
plt.scatter(range(len(list1)), list1, color='r', marker='o', label='List 1')
plt.scatter(range(len(list2)), list2, color='b', marker='o', label='List 2')
plt.legend()
plt.show()