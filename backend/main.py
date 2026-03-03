from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, Request
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
    "metrics": {},
    "portfolio": {},
    "isRunning": False,
    "algo_params": {
        "rsi_period": algo.rsi_period,
        "macd_fast": algo.macd_fast,
        "macd_slow": algo.macd_slow,
        "macd_signal": algo.macd_signal,
        "bb_period": algo.bb_period,
        "bb_std": algo.bb_std,
        "interval": algo.interval,
        "leverage": algo.leverage,
        "take_profit": algo.take_profit,
        "stop_loss": algo.stop_loss
    }
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

            # 2. Update Portfolio Value & Check Liquidations/SL/TP
            engine.check_liquidations_and_limits(current_prices, algo.stop_loss, algo.take_profit)
            latest_state["portfolio"] = engine.get_portfolio_value(current_prices)

            # 3. Analyze Data and Generate Signals
            signals = {}
            metrics = {}
            for pair in TRADE_PAIRS:
                # Need sufficient historical data for MA/RSI/Bollinger Bands
                data_list = gateio.get_candlesticks(pair, interval=algo.interval, limit=100)
                data_with_indicators = algo.add_indicators(data_list)
                signal = algo.evaluate(data_with_indicators)
                signals[pair] = signal

                # Extract latest metrics for UI
                if data_with_indicators and 'rsi' in data_with_indicators[-1]:
                    latest = data_with_indicators[-1]
                    metrics[pair] = {
                        "rsi": float(latest.get('rsi') or 0),
                        "macd": float(latest.get('macd') or 0),
                        "macd_signal": float(latest.get('macd_signal') or 0),
                        "bb_low": float(latest.get('bb_low') or 0),
                        "bb_high": float(latest.get('bb_high') or 0),
                    }

                # 4. Execute Trades
                current_price = float(tickers[pair]['last'])
                asset = pair.split('_')[0]

                # Simple portfolio sizing logic: allocate fixed margin per trade
                margin_amount_usd = 25.0

                # Close opposite positions or identical signals handled by engine logic loosely
                # If we get a SHORT signal but we are LONG, close the LONG first.
                current_position = engine.positions.get(pair)

                if signal == 'LONG':
                    if current_position and current_position.position_type == 'SHORT':
                        engine.close_position(pair, current_price, reason="SIGNAL_REVERSAL")

                    if not engine.positions.get(pair): # Open if no position
                        engine.open_position(pair, 'LONG', current_price, margin_amount=margin_amount_usd, leverage=algo.leverage)

                elif signal == 'SHORT':
                    if current_position and current_position.position_type == 'LONG':
                        engine.close_position(pair, current_price, reason="SIGNAL_REVERSAL")

                    if not engine.positions.get(pair): # Open if no position
                        engine.open_position(pair, 'SHORT', current_price, margin_amount=margin_amount_usd, leverage=algo.leverage)

            latest_state["signals"] = signals
            latest_state["metrics"] = metrics

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

@app.post("/api/params")
async def update_params(request: Request):
    """Update algorithm parameters."""
    params = await request.json()
    algo.update_params(params)
    # Update global state to broadcast back to UI
    latest_state["algo_params"] = {
        "rsi_period": algo.rsi_period,
        "macd_fast": algo.macd_fast,
        "macd_slow": algo.macd_slow,
        "macd_signal": algo.macd_signal,
        "bb_period": algo.bb_period,
        "bb_std": algo.bb_std,
        "interval": algo.interval,
        "leverage": algo.leverage,
        "take_profit": algo.take_profit,
        "stop_loss": algo.stop_loss
    }
    logger.info(f"Updated Algo Params: {latest_state['algo_params']}")
    return {"status": "success", "message": "Parameters updated"}

@app.get("/api/historical/{pair}")
def get_historical_data(pair: str, interval: str = "1m", limit: int = 200):
    """Get raw historical data for custom charting."""
    import datetime
    # Use the globally configured interval if none explicitly passed, or let user request specific
    use_interval = interval if interval else algo.interval
    data = gateio.get_candlesticks(pair, interval=use_interval, limit=limit)
    if not data:
        return []

    # Calculate indicators
    data = algo.add_indicators(data)

    # Convert timestamps to string and clean NaNs
    for d in data:
        d['timestamp'] = datetime.datetime.fromtimestamp(d['timestamp']).strftime('%H:%M:%S')
        for k, v in d.items():
            if v is None:
                d[k] = 0.0

    return data

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
