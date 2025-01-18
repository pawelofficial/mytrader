
from ms.data import Data
import numpy as np 
from scipy.optimize import minimize 
import pandas as pd 


class Strategy:
    def __init__(self,data:Data):
        self.data=data
        


    def optimize(self, method='nelder-mead', dim=1, options=None, stop_ratio=0.01, N=10, search_span=20):
        if options is None:
            options = {'maxiter': 1000, 'maxfev': 2000}

        def f(params):
            return -self.calculate_profit_scalp(self.strategy(params=params))

        
        best_best_result=None
        while True:
            best_res=None 
            for _ in range(N):
                init_guess = np.random.uniform(-search_span, search_span, size=dim)
                res = minimize(f, init_guess, method=method, options=options)

                if best_res is None or -res.fun>-best_res.fun:
                    best_res=res
                
                print("params:", res.x)
                print("profit:", -res.fun)
            
            print("    best params:", best_res.x)
            print("    best profit:", -best_res.fun)
            
            if best_best_result is None: # is the best result is None set current best result as the best result 
                best_best_result=best_res
            elif abs ( 1 - best_res.fun/best_best_result.fun ) < stop_ratio: # if best result and the best result are close then stop 
                print('found')
                break
            elif -best_res.fun>-best_best_result.fun:                          # if best result is better than the best result set it as the best result
                best_best_result=best_res


        print("     the best params:", best_best_result.x)
        print("     the best profit:", -best_best_result.fun)





    def __save(self,index,save,**kwargs):
        if save:
            for key,value in kwargs.items():
                self.data.df.at[index, key] = value


    def __save_prep(self,save  ):
        if save:
            self.data.df[f'total_profit']=0
            self.data.df[f'position']=''
            self.data.df[f'shares']=0
            self.data.df[f'capital']=0
        

        
    def calculate_profit(self,sig,price_ser=None,save  = False ):
        self.__save_prep(save) # if save passed prepare self.data.df for saving data 
        initial_capital,shares = 100.0,0
        capital=initial_capital

        if price_ser is None:
            price_ser=self.data.df['close']
            
        for i, row in sig.items():
            signal = sig[i]
            price =price_ser[i]
            # Buy
            if signal == 1 and shares == 0:
                shares = capital / price
                capital = 0
                self.__save(i,save,price=price,position=f'LONG',shares=shares,capital=capital)

            # Sell
            if signal == 0 and shares > 0:
                capital = shares * price
                shares = 0
                self.__save(i,save,price=price,position=f'SHORT',shares=shares,capital=capital)
                    
            current_value=capital if shares==0 else shares*price
            if current_value<0:
                print('error')

            self.__save(i,save,total_profit=current_value-initial_capital)
            
        return current_value-initial_capital


    def calculate_profit_scalp(self, sig, price_ser=None, save=False, scalp_ratio=0.5):
        """
        Calculate profit based on scalping strategy.

        Parameters:
        - sig: pandas Series with signals (1 for LONG, 0 for SHORT)
        - price_ser: pandas Series with price data (defaults to 'close' prices)
        - save: bool, whether to save transaction details
        - scalp_ratio: float, fraction of capital to use per trade (e.g., 0.1 for 10%)

        Returns:
        - total_profit: float, total profit/loss from the strategy
        """
        self.__save_prep(save)  # Prepare data if save is True
        initial_capital = 100.0
        capital = initial_capital
        total_profit=0
        shares = 0
        position = 'NONE'  # Possible values: 'LONG', 'SHORT', 'NONE'

        if price_ser is None:
            price_ser = self.data.df['close']

        for i, signal in sig.items():
            # Calculate scalp as a fraction of current capital
            scalp = scalp_ratio * capital
            scalp = min(scalp, capital,initial_capital)  # Ensure scalp does not exceed capital

            price = price_ser[i]

            # Debugging Statements (Can be uncommented for detailed tracing)
            # print(f"Date: {i}, Signal: {signal}, Price: {price}")
            # print(f"Current Position: {position}, Shares: {shares}, Capital: {capital}, Scalp: {scalp}")

            # Skip if the signal is the same as the current position
            if signal == 1 and position == 'LONG':
                self.__save(i, save, price=price, position='NONE', shares=shares, capital=capital, position_size=0,total_profit=total_profit)

            if signal == 0 and position == 'SHORT':
                  # Already in SHORT, skip
                self.__save(i, save, price=price, position='NONE', shares=shares, capital=capital, position_size=0,total_profit=total_profit)

            # Enter LONG Position
            if signal == 1 and position != 'LONG':
                position = 'LONG'
                shares = scalp / price if price != 0 else 0  # Avoid division by zero
                invested_amount = shares * price
                capital -= invested_amount  # Deduct the invested capital
                self.__save(i, save, price=price, position='LONG', shares=shares, capital=capital, position_size=invested_amount)
                # print(f"Entered LONG: Shares={shares}, Invested={invested_amount}, Capital={capital}")

            # Exit LONG Position and Enter SHORT Position
            elif signal == 0 and position == 'LONG' and shares > 0:
                proceeds = shares * price
                capital += proceeds  # Add the proceeds from selling shares
                self.__save(i, save, price=price, position='SHORT', shares=0, capital=capital, position_size=proceeds)
                shares = 0
                position = 'SHORT'
                # print(f"Exited LONG and Entered SHORT: Proceeds={proceeds}, Capital={capital}")

            # Calculate Current Value
            current_value = capital + (shares * price)

            # Error Handling
            if current_value < 0:
                print(f'Error: Negative portfolio value on {i}. Current Value: {current_value}')
                # Optionally, raise an exception or handle it accordingly
                # raise ValueError(f'Negative portfolio value on {i}')

            # Save Total Profit
            self.__save(i, save, total_profit=current_value - initial_capital)
            total_profit=current_value - initial_capital

        # Final Portfolio Valuation
        final_price = price_ser.iloc[-1]
        final_current_value = capital + (shares * final_price)
        total_profit = final_current_value - initial_capital
        return total_profit


    def old_calculate_profit_scalp(self,sig,price_ser=None,save  = False ):
        self.__save_prep(save) # if save passed prepare self.data.df for saving data 
        initial_capital,shares = 100.0,0
        capital=initial_capital

        if price_ser is None:
            price_ser=self.data.df['close']
            
        position='SHORT'
        scalp=initial_capital 
        for i, row in sig.items():
            scalp  = min(scalp, capital )
            
            signal = sig[i]
            price =price_ser[i]
            
            
            if signal == 1 and position == 'LONG':
                continue  # Already in LONG, skip
            if signal == 0 and position == 'SHORT':
                continue  # Already in SHORT, skip
            # Buy
            if signal == 1 and position =='SHORT':
                position='LONG'
                shares = scalp  / price 
                capital = capital-scalp 
                self.__save(i,save,price=price,position=f'LONG',shares=shares,capital=capital,position_size=scalp)

            # Sell
            if signal == 0 and shares > 0 and position=='LONG':
                position='SHORT'
                _ = shares * price
                shares = 0
                capital = capital + _
                
                self.__save(i,save,price=price,position=f'SHORT',shares=shares,capital=capital,position_size=_)
                    
            current_value=capital if shares==0 else shares*price
            if current_value<0:
                print('error')

            self.__save(i,save,total_profit=current_value-initial_capital)
            
        return current_value-initial_capital
    
    def strategy(self,col1='ema_10',col2='ema_20',col3='ema_10_der',sign='<',params=[0]):
        #ser = self.data.df[col1] - self.data.df[col2] + params[0] * self.data.df[col3] + params[1] * self.data.df[col3]**2 + params[2] * self.data.df[col3]**3
        ser = self.data.df[col1] - self.data.df[col2]
        for i, param in enumerate(params):
            ser += param * self.data.df[col3]**(i+1)
        if sign =='>':
            sig=ser.apply(lambda x: 1 if x>0 else 0)
        else:        
            sig=ser.apply(lambda x: 1 if x<0 else 0)
        return sig
    
    def calculate_profit_all_in(self, signal_column='ema_signal', price_column='close'):
        self.data.df[f'total_profit_{signal_column}'] = 0
        initial_capital = 100.0
        capital = initial_capital
        shares = 0
        current_value=initial_capital
        self.data.df['position']=''
        for i, row in self.data.df.iterrows():
            signal = row[signal_column]
            price = row[price_column]
            dt=row['datetime']
            # Buy (all in)
            if signal == 1 and shares == 0:
                print('buying ',current_value, f'price {price } date {dt} ')
                self.data.df.at[i,'position']='LONG'
                shares = capital / price
                capital = 0

            # Sell (all out)
            if signal == 0 and shares > 0:
                print('selling',current_value, f'price {price } date {dt} ')
                self.data.df.at[i,'position']='SHORT'
                capital = shares * price
                shares = 0

            # Track running profit
            current_value = capital if shares == 0 else shares * price
            if current_value<0:
                print('error')
            self.data.df.at[i, f'total_profit_{signal_column}'] = current_value - initial_capital

        return self.data.df[f'total_profit_{signal_column}'].iloc[-1]
        
    def ema_strategy(self,ema1='ema_10',ema2='ema_20',sign='<'):
        if sign =='>':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]-x[ema2]>0 else 0,axis=1)
        elif sign=='<':
            self.data.df['ema_signal']=self.data.df.apply(lambda x: 1 if x[ema1]-x[ema2]<0 else 0,axis=1)
        
        self.data.df['ema_signal'].fillna(0, inplace=True)
        self.data.df['ema_signal_close']=self.data.df['close']*self.data.df['ema_signal']
        
        
        self.data._set_columns_as_attributes()
        

    
    