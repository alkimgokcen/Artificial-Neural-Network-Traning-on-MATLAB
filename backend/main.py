from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import time
import json
import logging
from typing import Dict, Any

from gateio_client import GateIOClient
from trading_algorithm import TradingAlgorithm
from paper_engine import PaperTradingEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingBot")

app = FastAPI(title="Crypto Trading Bot", description="Automated paper trading bot for BTC, ETH, SOL on Gate.io")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
TRADE_PAIRS = ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
gateio = GateIOClient()
algo = TradingAlgorithm()
engine = PaperTradingEngine(initial_balance=100.0)

# In-memory storage for latest stats
latest_state = {
    "prices": {},
    "signals": {},
    "portfolio": {},
    "isRunning": False
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"WebSocket send error: {e}")

manager = ConnectionManager()

async def run_bot_loop():
    """Background task that runs the trading bot continuously."""
    logger.info("Starting trading bot loop...")
    latest_state["isRunning"] = True

    while latest_state["isRunning"]:
        try:
            # 1. Fetch Latest Prices
            tickers = await gateio.get_multiple_tickers(TRADE_PAIRS)
            current_prices = {}
            for pair, data in tickers.items():
                if data and 'last' in data:
                    asset = pair.split('_')[0]
                    current_prices[asset] = float(data['last'])

            latest_state["prices"] = current_prices

            # 2. Update Portfolio Value
            latest_state["portfolio"] = engine.get_portfolio_value(current_prices)

            # 3. Analyze Data and Generate Signals
            signals = {}
            for pair in TRADE_PAIRS:
                # Need sufficient historical data for MA/RSI/Bollinger Bands
                df = gateio.get_candlesticks(pair, interval="1m", limit=100)
                df_with_indicators = algo.add_indicators(df)
                signal = algo.evaluate(df_with_indicators)
                signals[pair] = signal

                # 4. Execute Trades
                current_price = float(tickers[pair]['last'])
                asset = pair.split('_')[0]

                # Simple portfolio sizing logic: max 25% of initial balance per trade to diversify
                trade_amount_usd = 25.0

                if signal == 'BUY':
                    # Only buy if we have enough cash
                    if engine.balances.get('USDT', 0) >= trade_amount_usd:
                        success = engine.execute_trade(pair, 'BUY', current_price, amount_in_usd=trade_amount_usd)
                        if success:
                            logger.info(f"Bot Executed BUY for {pair}")
                elif signal == 'SELL':
                    # Only sell if we have the asset
                    if engine.balances.get(asset, 0) > 0:
                        success = engine.execute_trade(pair, 'SELL', current_price)
                        if success:
                             logger.info(f"Bot Executed SELL for {pair}")

            latest_state["signals"] = signals

            # Update portfolio after potential trades
            latest_state["portfolio"] = engine.get_portfolio_value(current_prices)
            latest_state["history"] = engine.get_trade_history()

            # Broadcast update via WebSocket
            await manager.broadcast(json.dumps(latest_state))

            # Sleep before next cycle (10 seconds for demo)
            await asyncio.sleep(10)

        except asyncio.CancelledError:
            logger.info("Bot loop cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in bot loop: {e}")
            await asyncio.sleep(5)  # Backoff on error

@app.on_event("startup")
async def startup_event():
    # Start bot loop in background
    asyncio.create_task(run_bot_loop())

@app.on_event("shutdown")
async def shutdown_event():
    latest_state["isRunning"] = False

# REST API Endpoints

@app.get("/api/state")
def get_state() -> Dict[str, Any]:
    """Get the current state of the trading bot."""
    return latest_state

@app.get("/api/history")
def get_history() -> list:
    """Get full trade history."""
    return engine.get_trade_history()

@app.post("/api/reset")
def reset_bot() -> Dict[str, str]:
    """Reset the paper trading engine to initial state."""
    global engine
    engine = PaperTradingEngine(initial_balance=100.0)
    logger.info("Trading engine reset to initial state.")
    return {"status": "success", "message": "Bot reset successfully"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps(latest_state))
        while True:
            # Keep connection alive, wait for client disconnect
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
