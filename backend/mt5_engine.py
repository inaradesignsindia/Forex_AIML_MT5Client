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
        time.sleep(1)

if __name__ == "__main__":
    run_engine()