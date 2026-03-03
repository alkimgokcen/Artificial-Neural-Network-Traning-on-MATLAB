import time
import json
import logging
import threading
from typing import Dict, Any
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

from gateio_client import GateIOClient
from trading_algorithm import TradingAlgorithm
from paper_engine import PaperTradingEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingBot")

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
    "history": [],
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

def run_bot_loop():
    """Background thread that runs the trading bot continuously."""
    logger.info("Starting trading bot loop...")
    latest_state["isRunning"] = True

    while latest_state["isRunning"]:
        try:
            # 1. Fetch Latest Prices (Synchronous)
            tickers = gateio.get_multiple_tickers(TRADE_PAIRS)
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
                if pair in tickers and 'last' in tickers[pair]:
                    current_price = float(tickers[pair]['last'])

                    # Simple portfolio sizing logic: allocate fixed margin per trade
                    margin_amount_usd = 25.0

                    current_position = engine.positions.get(pair)

                    if signal == 'LONG':
                        if current_position and current_position.position_type == 'SHORT':
                            engine.close_position(pair, current_price, reason="SIGNAL_REVERSAL")

                        if not engine.positions.get(pair):
                            engine.open_position(pair, 'LONG', current_price, margin_amount=margin_amount_usd, leverage=algo.leverage)

                    elif signal == 'SHORT':
                        if current_position and current_position.position_type == 'LONG':
                            engine.close_position(pair, current_price, reason="SIGNAL_REVERSAL")

                        if not engine.positions.get(pair):
                            engine.open_position(pair, 'SHORT', current_price, margin_amount=margin_amount_usd, leverage=algo.leverage)

            latest_state["signals"] = signals
            latest_state["metrics"] = metrics

            # Update portfolio after potential trades
            latest_state["portfolio"] = engine.get_portfolio_value(current_prices)
            latest_state["history"] = engine.get_trade_history()

            # Sleep before next cycle (10 seconds for demo)
            time.sleep(10)

        except Exception as e:
            logger.error(f"Error in bot loop: {e}")
            time.sleep(5)  # Backoff on error


class SimpleAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        # Allow CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/api/state':
            self._set_headers()
            self.wfile.write(json.dumps(latest_state).encode('utf-8'))

        elif path == '/api/history':
            self._set_headers()
            self.wfile.write(json.dumps(engine.get_trade_history()).encode('utf-8'))

        elif path.startswith('/api/historical/'):
            pair = path.split('/')[-1]
            query = dict(urllib.parse.parse_qsl(parsed_path.query))
            limit = int(query.get('limit', 100))

            import datetime
            data = gateio.get_candlesticks(pair, interval=algo.interval, limit=limit)
            if data:
                data = algo.add_indicators(data)
                for d in data:
                    d['timestamp'] = datetime.datetime.fromtimestamp(d['timestamp']).strftime('%H:%M:%S')
                    for k, v in d.items():
                        if v is None:
                            d[k] = 0.0
            else:
                data = []

            self._set_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        if self.path == '/api/reset':
            global engine
            engine = PaperTradingEngine(initial_balance=100.0)
            logger.info("Trading engine reset to initial state.")
            self._set_headers()
            self.wfile.write(b'{"status": "success", "message": "Bot reset successfully"}')

        elif self.path == '/api/params':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data)
            algo.update_params(params)

            # Update global state
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
            self._set_headers()
            self.wfile.write(b'{"status": "success", "message": "Parameters updated"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not Found"}')


def start_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    logger.info(f"Starting API Server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start bot loop in background thread
    bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
    bot_thread.start()

    # Start HTTP server
    start_server(8000)
