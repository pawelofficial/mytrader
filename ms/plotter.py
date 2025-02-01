from matplotlib import pyplot as plt
import os 
from ms.utils import setup_logger
from ms.data import Data
import numpy as np 
import pandas as pd 
import mplfinance as mpf

class Plotter:
    def __init__(self,df):
        self.df=df
        self.logger=setup_logger('plotter')
        self.logger.info('plotter object created')
        self.this_path = os.path.dirname(os.path.abspath(__file__)) 
        self.plots_path = os.path.join(self.this_path, 'plots')
        
    def simplest_scatter_plot(self,data : Data
                              ,xcol='datetime'
                              ,ycol='close'
                              ,ema_cols=None
                              ,signal_cols=[]
                              ,show=True
                              ,save=True
                              ,subplot=(False, ) # ( True, columnn_name)
                              ,start_date=None # 'start' # yyyy-mm-dd 
                              ,end_date=None#'1995-01-01' # yyyy-mm-dd  'today'
                              ,log_scale=False
                              ,fname='simplest_scatter_plot.png'): 
        if start_date is not None:
            if start_date=='start':
                start_date=self.df['datetime'].min()
            else:
                start_date=pd.to_datetime(start_date)
            self.df=self.df[self.df['datetime']>=start_date]

        if end_date is not None and end_date!='today':
            self.df=self.df[self.df['datetime']<=end_date]
            
        
        plt.scatter(self.df[xcol],self.df[ycol],marker='.',color='black' ) 
        plt.xlabel(xcol)
        plt.ylabel(ycol)
        colors = plt.cm.Blues(np.linspace(0.3, 1, len(ema_cols)))        
        # if ema cols are not none plot them as lines 
        if ema_cols:
            for col, color in zip(ema_cols, colors):
                plt.plot(self.df[xcol], self.df[col], label=col, color=color)
            plt.legend()
            
        if signal_cols:
            for signal_col in signal_cols:
                signal_mask=self.df[signal_col]==1
                plt.scatter(self.df[xcol][signal_mask],self.df[ycol][signal_mask],marker='.', color='green',label=signal_col)
                plt.legend()
        
        if subplot[0]:
            # plot on secondary y axis 
            ax2 = plt.twinx()
            if log_scale:
                ax2.set_yscale('log')
            ax2.plot(self.df[xcol], self.df[subplot[1]], label=subplot[1])
            ax2.legend()

        
        if show:
            plt.show()
        if save:
            plt.savefig(os.path.join(self.plots_path,fname))
            



    def candleplot(self, df=None, ser=None, date_column='datetime', signal_column_name='position',total_profit_column='total_profit',sig_bl_column='sig_bl'):
        if df is None:
            df = self.df.copy()
        if df.empty:
            raise ValueError("DataFrame is empty")
            
    
        required_columns = {'open', 'close', 'low', 'high', 'volume'}
        if not required_columns.issubset(df.columns.str.lower()):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
    
        # Ensure the DataFrame index is a DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.set_index(pd.to_datetime(df[date_column]), inplace=True)
    
        if signal_column_name not in df.columns:
            df['signal'] = 0  # Default to no signals

    
        # Create full-length series for buy and sell signals
        buy_signal = pd.Series(data=np.nan, index=df.index)
        sell_signal = pd.Series(data=np.nan, index=df.index)
    
        buy_indices = df[df[signal_column_name] == 'LONG'].index
        sell_indices = df[df[signal_column_name] == 'SHORT'].index
    
        buy_signal.loc[buy_indices] = df.loc[buy_indices, 'low'] - (df['low'].min() * 0.01)
        sell_signal.loc[sell_indices] = df.loc[sell_indices, 'high'] + (df['high'].min() * 0.01)
    
        # signal bl 
        #signal_bl_buy_indices = df[df[sig_bl_column].apply(lambda x: int(x)) == 1].index
        df[sig_bl_column] = pd.to_numeric(df[sig_bl_column], errors='coerce')
        signal_bl_buy = pd.Series(data=np.nan, index=df.index)
        signal_bl_sell= pd.Series(data=np.nan, index=df.index)



        # Identify indices where sig_bl_column indicates a buy signal (e.g., 1)
        signal_bl_buy_indices = df[df[sig_bl_column] == 1].index
        signal_bl_buy.loc[signal_bl_buy_indices] = df.loc[signal_bl_buy_indices, 'open'] - (df['open'].min() * 0.02)
    
        # Identify indices where 'sell' indicates a buy signal (e.g., 0)
        signal_bl_sell_indices = df[df[sig_bl_column] == 0].index
        signal_bl_sell.loc[signal_bl_sell_indices] = df.loc[signal_bl_sell_indices, 'open'] - (df['open'].min() * 0.02)
                
    
        # Create addplot for buy signals
        addplots = []
        if not buy_indices.empty:
            buy_markers = mpf.make_addplot(
                buy_signal,
                type='scatter',
                markersize=100,
                marker='^',
                color='g',
                label='Buy Signal'
            )
            addplots.append(buy_markers)
    
        # Create addplot for sell signals
        if not sell_indices.empty:
            sell_markers = mpf.make_addplot(
                sell_signal,
                type='scatter',
                markersize=100,
                marker='v',
                color='r',
                label='Sell Signal'
            )
            addplots.append(sell_markers)
        
        # signal_bl_buy_indices
        signal_bl_markers = mpf.make_addplot(
            signal_bl_buy,
            type='scatter',
            markersize=25,
            marker='^',
            color='orange',
            label='Signal BL Buy'
        )
        addplots.append(signal_bl_markers)
        
        # signal_bl_sell_indices
        signal_bl_markers = mpf.make_addplot(
            signal_bl_sell,
            type='scatter',
            markersize=25,
            marker='v',
            color='blue',
            label='Signal BL Buy'
        )
        addplots.append(signal_bl_markers)
            
        if total_profit_column:
            total_profit_line = mpf.make_addplot(
                df[total_profit_column],
                panel=1,
                color='b',
                secondary_y=True,
                ylabel='Total Profit',

            )
            addplots.append(total_profit_line)
    
    
        # Optional: Set the style of the plot
        style = mpf.make_mpf_style(
            base_mpf_style='yahoo',
            rc={'font.size': 10}
        )
    
        # Plot with addplots
        mpf.plot(
            df,
            type='candle',
            style=style,
            volume=True,
            addplot=addplots,
            title='Stock Candlestick Chart with Buy/Sell Signals',
            ylabel='Price',
            ylabel_lower='Volume',
            figsize=(12, 8),
            tight_layout=True
        )
        # add total profit line plot on secondary y axis 

    
    
        # Create a legend
        handles = []
        labels = []
        if not buy_indices.empty:
            handles.append(plt.Line2D([], [], marker='^', color='g', linestyle='None'))
            labels.append('Buy Signal')
        if not sell_indices.empty:
            handles.append(plt.Line2D([], [], marker='v', color='r', linestyle='None'))
            labels.append('Sell Signal')
    
        if handles:
            plt.legend(handles, labels, loc='upper left')



# Example usage
if __name__ == "__main__":
    # Sample data
    data = {
        'open': [100, 102, 101, 105],
        'close': [102, 101, 105, 107],
        'low': [99, 100, 100, 104],
        'high': [103, 103, 106, 108],
        'volume': [1000, 1500, 1200, 1300]
    }

    # Create a date range
    dates = pd.date_range(start='2023-01-01', periods=4, freq='D')

    # Create DataFrame
    df = pd.DataFrame(data, index=dates)

    # Plot the candlestick chart
    plot_candlestick(df)
    