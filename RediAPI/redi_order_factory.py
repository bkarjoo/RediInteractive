
import win32com.client
import pythoncom

account = "8AO07074"
exchange = "APEX QUIK"


class RediOrderFactory:
    
    def __init__(self):
        pass
    
    @staticmethod
    def set_account(acct):
        global account
        account = acct
    
    @staticmethod
    def order(side, symbol, quantity, price_type, price, tif, stop=0, acct=""):
        # Equity Order Entry Example
        # create an order object
        pythoncom.CoInitialize()
        o = win32com.client.Dispatch("REDI.ORDER")
    
        # set the order objects properties
        o.Side = side
        o.symbol = symbol
        o.Exchange = exchange
        o.Quantity = quantity
        o.PriceType = price_type
        if price_type == "Stop Limit":
            o.StopPrice = stop
        if price != 0:
            o.Price = price
    
        o.TIF = tif
        if acct == "":
            o.Account = account
        else:
            o.Account = acct
        o.Ticket = "Bypass"
        o.CustomerIndicator = "API"
    
        # Prepare a variable which can handle returned values from submit method of the order object.
        err = win32com.client.VARIANT(win32com.client.pythoncom.VT_BYREF | win32com.client.pythoncom.VT_VARIANT, None)
        transID = win32com.client.VARIANT(win32com.client.pythoncom.VT_BYREF | win32com.client.pythoncom.VT_VARIANT, None)
    
        # Send the order calling its submit method
        result = o.Submit2(transID, err)
    
        print result  # 'True' if order submission was successful; otherwise 'False'
        print err.value    # message from sumbi1
        print transID.value
        return result
    
    @staticmethod
    def generate_limit_order(qty, symbol, price, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        if price <= 0: 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Limit", price, "Day", 0, acct)
    
    @staticmethod
    def generate_opg_market_order(qty, symbol, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Market", 0, "OPG", 0, acct)
    
    @staticmethod
    def generate_opg_limit_order(qty, symbol, price, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        if price <= 0: 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Limit", price, "OPG", 0, acct)
    
    @staticmethod
    def generate_moc_order(qty, symbol, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Market Close", 0, "Day", 0, acct)
    
    @staticmethod
    def generate_loc_order(qty, symbol, price, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        if price <= 0: 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Limit Close", price, "Day", 0, acct)
    
    @staticmethod
    def generate_stop_limit_order(qty, symbol, stop_price, limit_price, acct=''):
        if qty == 0: 
            return False
        if symbol == "": 
            return False
        if limit_price <= 0: 
            return False
        if stop_price <= 0: 
            return False
        side = "Buy" if qty > 0 else "Sell Auto"
        return RediOrderFactory.order(side, symbol, abs(qty), "Stop Limit", limit_price, "Day", stop_price, acct)
