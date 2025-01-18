from matplotlib import pyplot as plt
import os 
from ms.utils import setup_logger
from ms.data import Data
import numpy as np 
import pandas as pd 

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
                              ,start_date='start' # yyyy-mm-dd 
                              ,end_date='1995-01-01' # yyyy-mm-dd  'today'
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
            