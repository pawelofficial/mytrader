import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from chronos import ChronosPipeline




pipeline = ChronosPipeline.from_pretrained(
  "amazon/chronos-t5-mini",
  device_map="cpu",
  torch_dtype=torch.bfloat16,
  token=TOKEN,
)


df = pd.read_csv("https://raw.githubusercontent.com/AileenNielsen/TimeSeriesAnalysisWithPython/master/data/AirPassengers.csv")
df=pd.read_csv('../data/BTC.csv')
start_index=100
end_index=300
df=df.iloc[start_index:end_index].copy()
df.reset_index(drop=True,inplace=True)

# calculate z values 
df['z']=(df['close']-df['close'].mean())/df['close'].std()


original_df=df.copy()
metric="#Passengers"
metric='z'
prediction_length = 20
df=df.iloc[:-prediction_length].copy()
# context must be either a 1D tensor, a list of 1D tensors,
# or a left-padded 2D tensor with batch as the first dimension
context = torch.tensor(df[metric])

forecast = pipeline.predict(context, prediction_length)  # shape [num_series, num_samples, prediction_length]

# visualize the forecast
forecast_index = range(len(df), len(df) + prediction_length)
low, median, high = np.quantile(forecast[0].numpy(), [0.05, 0.5, 0.95], axis=0)

plt.figure(figsize=(8, 4))
plt.plot(df[metric], color="royalblue", label="train data")
plt.plot(original_df[metric], color="green", label="historical data",alpha=0.5)
plt.plot(forecast_index, median, color="tomato", label="median forecast")
plt.fill_between(forecast_index, low, high, color="tomato", alpha=0.3, label="90% prediction interval")
plt.legend()
plt.grid()
plt.show()
