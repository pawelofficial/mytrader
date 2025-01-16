
from ms.data import Data




class Strategy:
    def __init__(self,data:Data):
        self.data=data
        self.df=data.df
        
        
    def calculate_profit_all_in(self, signal_column='ema_signal', price_column='close'):
        self.df[f'total_profit_{signal_column}'] = 0
        initial_capital = 100.0
        capital = initial_capital
        shares = 0
        self.df['position']=''
        for i, row in self.df.iterrows():
            signal = row[signal_column]
            price = row[price_column]

            # Buy (all in)
            if signal == 1 and shares == 0:
                #print('buying')
                self.df.at[i,'position']='LONG'
                shares = capital / price
                capital = 0

            # Sell (all out)

            
            if signal == 0 and shares > 0:
                #print('selling')
                self.df.at[i,'position']='SHORT'
                capital = shares * price
                shares = 0

            # Track running profit
            current_value = capital if shares == 0 else shares * price
            self.df.at[i, f'total_profit_{signal_column}'] = current_value - initial_capital

        return self.df[f'total_profit_{signal_column}'].iloc[-1]

        

    def ema_strategy(self,ema1='ema_10',ema2='ema_20',sign='>'):
        if sign =='>':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]>x[ema2] else 0,axis=1)
        elif sign=='<':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]<x[ema2] else 0,axis=1)
        
        self.data.df['ema_signal'].fillna(0, inplace=True)
        self.data.df['ema_signal_close']=self.data.df['close']*self.data.df['ema_signal']
        self.data._set_columns_as_attributes()
        
        