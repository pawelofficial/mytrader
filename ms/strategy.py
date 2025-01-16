
from ms.data import Data




class Strategy:
    def __init__(self,data:Data):
        self.data=data
        self.df=data.df
        
        
    def calculate_profit(self, signal_column='ema_signal', price_column='close'):
        """
        Calculate profit based on buy/sell signals in a DataFrame.

        Parameters:
            df (pd.DataFrame): DataFrame containing stock data.
            signal_column (str): Name of the column with buy (1) and sell (0) signals.
            price_column (str): Name of the column with stock prices.

        Returns:
            float: Total profit or loss.
        """
        self.df[f'total_profit_{signal_column}']=0
        # Initialize variables
        holding = 0  # Tracks whether we currently hold stock (1 if holding, 0 if not)
        total_profit = 0.0  # Tracks the total profit
        last_buy_price = 0.0  # Price at which the last buy occurred

        for index, row in self.df.iterrows():
            signal = row[signal_column]
            price = row[price_column]
            if signal == 1 and holding == 0:  # Buy signal and not holding
                last_buy_price = price
                
                holding = 1
            elif signal == 0 and holding == 1:  # Sell signal and holding
                total_profit += price - last_buy_price
                holding = 0
            self.df.at[index,f'total_profit_{signal_column}']=total_profit

        self.data._set_columns_as_attributes()
        return total_profit

    def ema_strategy(self,ema1='ema_10',ema2='ema_20',sign='<'):
        if sign =='>':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]>x[ema2] else 0,axis=1)
        elif sign=='<':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]<x[ema2] else 0,axis=1)
        self.data.df['ema_signal'].fillna(0, inplace=True)
        self.data.df['ema_signal_close']=self.data.df['close']*self.data.df['ema_signal']
        self.data._set_columns_as_attributes()
        
        