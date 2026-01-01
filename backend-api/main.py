from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
import os
from typing import Optional
import time

app = FastAPI(title="Forex AI API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
client = MongoClient(os.environ["MONGO_URL"])
db = client.forex_db

# Models
class TradeCommand(BaseModel):
    symbol: str
    action: str  # 'buy' or 'sell'
    order_type: str  # 'market', 'limit', 'stop'
    volume: float
    take_profit: int = 0
    stop_loss: int = 0
    trailing_stop: bool = False
    price: Optional[float] = None

@app.get("/api/live-state")
async def get_live_state():
    """Get current live trading state"""
    state = db.live_state.find_one({"id": "current_state"})
    if not state:
        return {"message": "No live data available"}
    return state

@app.post("/api/trade")
async def place_trade(trade: TradeCommand):
    """Place a manual trade"""
    trade_dict = trade.dict()
    trade_dict.update({
        "timestamp": time.time(),
        "status": "pending"
    })

    result = db.trade_commands.insert_one(trade_dict)
    return {"message": "Trade command submitted", "id": str(result.inserted_id)}

@app.get("/api/trade-commands")
async def get_trade_commands(limit: int = 10):
    """Get recent trade commands"""
    commands = list(db.trade_commands.find().sort("timestamp", -1).limit(limit))
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
    return commands

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)