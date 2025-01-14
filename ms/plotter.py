from matplotlib import pyplot as plt
import os 
from ms.utils import setup_logger
from ms.data import Data



class Plotter:
    def __init__(self):
        self.df=None
        self.logger=setup_logger('plotter')
        self.logger.info('plotter object created')
        self.this_path = os.path.dirname(os.path.abspath(__file__)) 
        self.plots_path = os.path.join(self.this_path, 'plots')
        
    def simplest_scatter_plot(self,data : Data
                              ,xcol='datetime'
                              ,ycol='close'
                              ,show=True
                              ,save=True
                              ,fname='simplest_scatter_plot.png'): 
        plt.scatter(data.df[xcol],data.df[ycol]) 
        plt.xlabel(xcol)
        plt.ylabel(ycol)
        if show:
            plt.show()
        if save:
            plt.savefig(os.path.join(self.plots_path,fname))
            