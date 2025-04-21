from binance.client import Client
import os
import dotenv
import numpy as np 
import time 
from ms.utils import setup_logger
dotenv.load_dotenv()



class Trade:
    def __init__(self):
        self.API_KEY=os.environ.get('API_KEY')
        self.API_SECRET=os.environ.get('API_SECRET')
        self.client = Client(self.API_KEY, self.API_SECRET)
        
        self.symbols=['USDC','BTC']
        self.pairs={'bitek':'BTCUSDC'}
        self.trade_symbols={'stable':'USDC','crypto':'BTC'}
        self.logger=setup_logger('trade')
        self.last_order={'side':None,'quantity':None,'status':None,'order':None}
        self.format_quantity = lambda n: '{:.8f}'.format(n)  # Format to 8 decimal places
        

# Function to get account balance for a specific asset
    def check_portfolio(self):
        portfolio={}
        for symbol in self.symbols:
            balance = self.client.get_asset_balance(asset=symbol)
            portfolio[symbol] = float(balance['free'])
        return portfolio            

    def get_balance(self,asset):
        assert asset in self.symbols
        balance = self.client.get_asset_balance(asset=asset)
        return float(balance['free'])

    def get_price(self,pair):
        assert pair in self.pairs.keys()
        price = self.client.get_symbol_ticker(symbol=self.pairs[pair])
        return float(price['price'])

    def calculate_amo_to_buy(self,asset,pair
                             ,dollars_to_spend=20 # how much in dollars you want to spend , precendence over capital_ratio
                             ,capital_ratio=1
                             ,all_in_when_negative = (True,'capital_ratio',0.95) # to do - goo all in if capital_ratio and rounding caused too big of an order 
                             ,N=6
                             ): # how much of your capital you want to spend
        capital=self.get_balance(asset)
        dollars_to_spend=dollars_to_spend or capital * capital_ratio
        #assert dollars_to_spend<=capital, f'not enough capital {dollars_to_spend} > {capital}'
        
        asset_price=self.get_price(pair)
        asset_amo=np.round(dollars_to_spend/asset_price,N) # this introduced a real possibility of not being able to buy the asset
        dollars_spent=asset_price*asset_amo
        leftovers=capital-dollars_spent
        dic={'capital':capital,'dollars_to_spend':dollars_to_spend,'asset_price':asset_price,'asset_amo':asset_amo,'dollars_spent':dollars_spent,'leftovers':leftovers,'inputs':{'dollars_to_spend':dollars_to_spend,'capital_ratio':capital_ratio,'all_in_when_negative':all_in_when_negative}}
        if leftovers<0 and all_in_when_negative[0]:
            if all_in_when_negative[1]=='capital_ratio':     
                print('trying again on capital_ratio ',dic)
                new_ratio=all_in_when_negative[2]
                all_in_when_negative = (True,'capital_ratio',new_ratio*0.99)
                return self.calculate_amo_to_buy(asset,pair,dollars_to_spend=None,capital_ratio=new_ratio,all_in_when_negative=all_in_when_negative)
            elif all_in_when_negative[1]=='dollars_to_spend':
                print('trying again on dollars_to_spend ',dic)
                delta=all_in_when_negative[2]
                return self.calculate_amo_to_buy(asset,pair,dollars_to_spend=dollars_to_spend-delta,capital_ratio=1,all_in_when_negative=all_in_when_negative)
                
        elif leftovers<0 and all_in_when_negative[0]==False:
            assert leftovers>0, f'not enough capital {leftovers} > 0'            
        
        print(dic)
        return dic

    def get_lot_size(self,pair):
        info = self.client.get_symbol_info(pair)
        filters = info['filters']
        for f in filters:
            if f['filterType'] == 'LOT_SIZE':
                return float(f['stepSize']),float(f['minQty'])
        return None

    # Function to place a market buy order
    def buy(self, pair, dollar_quantity):
        if dollar_quantity<0:
            print('not supporting all in yet')
            return 
        dic=self.calculate_amo_to_buy(self.trade_symbols['stable'],'bitek',dollars_to_spend=dollar_quantity,capital_ratio=1,all_in_when_negative = (True,'dollars_to_spend',1))
        quantity=dic['asset_amo']
        
        return self.place_market_buy_order(pair, quantity)
    
    def sell(self, pair, quantity):
        if quantity==-1:
            quantity=self.get_balance(self.trade_symbols['crypto'])
        return self.place_market_sell_order(pair, quantity)
    
    def place_market_sell_order(self, pair, quantity):
        # Get the step size and minimum quantity for the trading pair
        step_size, minQty = self.get_lot_size(self.pairs[pair])

        # Ensure the quantity is adjusted to comply with LOT_SIZE
        order_quantity = max((quantity // step_size) * step_size, minQty)
        order = None
        try:
            # Place the market sell order using the adjusted quantity
            order = self.client.order_market_sell(
                symbol=self.pairs[pair],
                quantity=self.format_quantity(order_quantity)
            )
            self.logger.info(f"Sell Order placed:\n {order}")
            self.last_order={'side':'SELL','quantity':order_quantity,'status':'OK','order':order}
        except Exception as e:
            self.last_order={'side':'SELL','quantity':order_quantity,'status':'ERROR','order':order}
            self.logger.error(f"Error placing order: {e}")
            print("Error placing order:", e)

        # check amounts afterwards 
        time.sleep(3)
        usdt_amo=self.get_balance(self.trade_symbols['stable'])
        btc_amo=self.get_balance(self.trade_symbols['crypto'])
        
        return order,{'stable':usdt_amo,'crypto':btc_amo}
    
    def place_market_buy_order(self, pair, quantity):
        # Get the step size and minimum quantity for the trading pair
        step_size, minQty = self.get_lot_size(self.pairs[pair])

        print(self.format_quantity(quantity))
        # Ensure the quantity is adjusted to comply with LOT_SIZE
        order_quantity = max((quantity // step_size) * step_size, minQty)
        print(self.format_quantity(order_quantity),minQty)
        order = None
        try:
            # Place the market buy order using the adjusted quantity
            order = self.client.order_market_buy(
                symbol=self.pairs[pair],
                quantity=self.format_quantity(order_quantity)
            )
 
            self.logger.info(f"Order placed:\n {order}")
            self.last_order={'side':'BUY','quantity':order_quantity,'status':'OK','order':order}
        except Exception as e:
            self.last_order={'side':'BUY','quantity':order_quantity,'status':'ERROR','order':order}
            self.logger.error(f"Error placing order: {e}")
            print("Error placing order:", e)

        # Wait for a moment and check balances
        time.sleep(3)
        usdt_amo = self.get_balance(self.trade_symbols['stable'])
        btc_amo = self.get_balance(self.trade_symbols['crypto'])

        return order, {'stable': usdt_amo, 'crypto': btc_amo}


#Order placed: {'symbol': 'BTCUSDT', 'orderId': 35502221867, 'orderListId': -1, 'clientOrderId': 'x-HNA2TXFJd5dcf0555eb73ee463459e', 'transactTime': 1737304377833, 'price': '0.00000000', 'origQty': '0.00019000', 'executedQty': '0.00019000', 'origQuoteOrderQty': '0.00000000', 'cummulativeQuoteQty': '19.96178380', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'workingTime': 1737304377833, 'fills': [{'price': '105062.02000000', 'qty': '0.00019000', 'commission': '0.00000019', 'commissionAsset': 'BTC', 'tradeId': 4426925936}], 'selfTradePreventionMode': 'EXPIRE_MAKER'}

# Example usage
if __name__ == "__main__":
    tb=ms.trade_binance.Trade()
    btc=tb.get_balance('BTC')
    usdt=tb.get_balance('USDT')
    print(usdt,btc)

    if 1: # buying 
        o,amos=tb.buy('bitek', 20)
        print(amos)
    if 1: # selling
        qty=tb.get_balance('BTC')
        o,amos=tb.sell('bitek',qty)
        print(amos)
    #print(amos)
