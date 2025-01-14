from matplotlib import pyplot as plt

from ms.utils import setup_logger
from ms.data import Data



class Plotter:
    def __init__(self):
        self.df=None
        self.logger=setup_logger('plotter')
        self.logger.info('plotter object created')
        
    def simplest_scatter_plot(self,data :Data,xcol='unixtime',ycol='close'): 
        plt.scatter(data.df[xcol],data.df[ycol]) 
        plt.xlabel(x)
        plt.ylabel(y)
        plt.show()