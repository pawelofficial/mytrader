from matplotlib import pyplot as plt
import os 
from ms.utils import setup_logger
from ms.data import Data



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
                              ,signal_col=None
                              ,show=True
                              ,save=True
                              ,subplot=(False, ) # ( True, columnn_name)
                              ,start_date='2024-01-01' # yyyy-mm-dd 
                              ,end_date='today'
                              ,fname='simplest_scatter_plot.png'): 
        if start_date is not None:
            self.df=self.df[self.df['datetime']>=start_date]

        if end_date is not None and end_date!='today':
            self.df=self.df[self.df['datetime']<=end_date]
            
        
        plt.scatter(self.df[xcol],self.df[ycol]) 
        plt.xlabel(xcol)
        plt.ylabel(ycol)
        
        # if ema cols are not none plot them as lines 
        if ema_cols:
            for col in ema_cols:
                plt.plot(self.df[xcol],self.df[col],label=col)
            plt.legend()
        if signal_col:
            signal_mask=self.df[signal_col]==1
            plt.scatter(self.df[xcol][signal_mask],self.df[ycol][signal_mask],marker='x', color='red',label=signal_col)
            plt.legend()
        
        if subplot[0]:
            # plot on secondary y axis 
            plt.twinx()
            plt.plot(self.df[xcol],self.df[subplot[1]],label=subplot[1])
            plt.legend()
        
        if show:
            plt.show()
        if save:
            plt.savefig(os.path.join(self.plots_path,fname))
            