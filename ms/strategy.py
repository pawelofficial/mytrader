
from ms.data import Data
import numpy as np 
from scipy.optimize import minimize 
import pandas as pd 


class Strategy:
    def __init__(self,data:Data):
        self.data=data
        
    def optimize(self, method='nelder-mead', dim=1, options=None,stop_ratio=0.01,N=20,search_span=-10 ):
        if options is None:
            options = {'maxiter': 1000, 'maxfev': 2000}

        def f(params):
            return -self.calculate_profit(self.strategy(params=params))

        best_res = None
        prev_best_fun = None  # track the previous fun (not the negative)

        while True:
            
            for _ in range(N):
                init_guess = np.random.uniform(-search_span, search_span, size=dim)
                res = minimize(f, init_guess, method=method, options=options)
                if best_res is None or res.fun < best_res.fun:
                    best_res = res

            # compare new best vs previous
            print('next iteration',best_res.fun , prev_best_fun )
            if prev_best_fun is not None:
                ratio = best_res.fun / prev_best_fun
                if 1-stop_ratio < ratio < 1+stop_ratio:  # no big improvement
                    break

            prev_best_fun = best_res.fun

        print("Best params:", best_res.x)
        print("Max profit:", -best_res.fun)



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

        
    def calculate_profit(self,sig,price_ser=None,save  = True ):
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
                self.__save(i,save,price=price,position=f'LONG',shares=shares,capital=capital)
                    
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
        

    
    