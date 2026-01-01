import MetaTrader5 as mt5
from pymongo import MongoClient
import time
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Config
MONGO_URL = "mongodb+srv://inaradesignsindia:Singlelot5@cluster0.luis5th.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client.forex_db

def get_ai_signal(symbol):
    # Dummy ML logic: replace with your trained model
    return "BUY" if time.time() % 2 == 0 else "SELL"

def run_engine():
    if not mt5.initialize():
        return
    
    while True:
        account = mt5.account_info()._asdict()
        positions = [p._asdict() for p in mt5.positions_get()]
        
        payload = {
            "id": "current_state",
            "account": account,
            "positions": positions,
            "suggestion": get_ai_signal("EURUSD"),
            "ai_confidence": 85,
            "timestamp": time.time()
        }
        
        db.live_state.update_one({"id": "current_state"}, {"$set": payload}, upsert=True)

        # Check for trade commands
        pending_trades = db.trade_commands.find({"status": "pending"})
        for trade in pending_trades:
            try:
                execute_trade(trade)
                db.trade_commands.update_one({"_id": trade["_id"]}, {"$set": {"status": "executed", "executed_at": time.time()}})
            except Exception as e:
                print(f"Failed to execute trade {trade['_id']}: {e}")
                db.trade_commands.update_one({"_id": trade["_id"]}, {"$set": {"status": "failed", "error": str(e)}})

        time.sleep(1)

def execute_trade(trade):
    symbol = trade["symbol"]
    action = trade["action"]  # 'buy' or 'sell'
    order_type = trade["order_type"]  # 'market', 'limit', 'stop'
    volume = trade["volume"]
    take_profit = trade.get("take_profit", 0)
    stop_loss = trade.get("stop_loss", 0)
    trailing_stop = trade.get("trailing_stop", False)

    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        raise Exception(f"Failed to get tick data for {symbol}")

    if action == "buy":
        price = tick.ask if order_type == "market" else trade.get("price", tick.ask)
        sl = price - (stop_loss * 0.0001) if stop_loss > 0 else 0
        tp = price + (take_profit * 0.0001) if take_profit > 0 else 0
    else:  # sell
        price = tick.bid if order_type == "market" else trade.get("price", tick.bid)
        sl = price + (stop_loss * 0.0001) if stop_loss > 0 else 0
        tp = price - (take_profit * 0.0001) if take_profit > 0 else 0

    # Determine order type
    if order_type == "market":
        order_type_mt5 = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
    elif order_type == "limit":
        order_type_mt5 = mt5.ORDER_TYPE_BUY_LIMIT if action == "buy" else mt5.ORDER_TYPE_SELL_LIMIT
    elif order_type == "stop":
        order_type_mt5 = mt5.ORDER_TYPE_BUY_STOP if action == "buy" else mt5.ORDER_TYPE_SELL_STOP

    # Prepare order
    request = {
        "action": mt5.TRADE_ACTION_DEAL if order_type == "market" else mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_mt5,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Manual Trade from Dashboard",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send order
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        raise Exception(f"Order failed: {result.comment}")

    print(f"Trade executed: {action} {volume} {symbol} at {price}")

if __name__ == "__main__":
    run_engine()