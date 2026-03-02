import datetime
from typing import Dict, List, Optional
import json

class TradeInfo:
    def __init__(self, timestamp: float, pair: str, side: str, amount: float, price: float, total: float):
        self.timestamp = timestamp
        self.pair = pair
        self.side = side # 'BUY' or 'SELL'
        self.amount = amount
        self.price = price
        self.total = total

    def to_dict(self):
        return {
            "timestamp": datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "pair": self.pair,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
            "total": self.total
        }

class PaperTradingEngine:
    def __init__(self, initial_balance: float = 100.0, base_currency: str = "USDT"):
        """Initialize the trading engine with a starting balance."""
        self.base_currency = base_currency
        self.balances: Dict[str, float] = {base_currency: initial_balance}
        self.initial_balance = initial_balance
        self.trades: List[TradeInfo] = []

        # We will keep track of average entry prices to calculate PnL
        self.avg_entry_prices: Dict[str, float] = {}

    def get_balance(self) -> Dict[str, float]:
        """Return all non-zero balances."""
        return {asset: amount for asset, amount in self.balances.items() if amount > 0}

    def execute_trade(self, pair: str, side: str, current_price: float, amount_in_usd: Optional[float] = None) -> bool:
        """
        Execute a buy or sell trade at the current market price.
        Pair format: e.g. 'BTC_USDT'
        side: 'BUY' or 'SELL'
        amount_in_usd: If buying, how much USD to spend. If selling, it sells all of the asset by default if None.
        """
        asset, quote = pair.split('_')

        if quote != self.base_currency:
            print(f"Unsupported quote currency: {quote}")
            return False

        if side == 'BUY':
            if amount_in_usd is None:
                # Default behavior: use a fraction of available balance (e.g. 50%) or a fixed amount
                available_usd = self.balances.get(self.base_currency, 0)
                amount_in_usd = available_usd * 0.5 # use 50% of available cash

            if amount_in_usd <= 0 or self.balances.get(self.base_currency, 0) < amount_in_usd:
                print(f"Insufficient {self.base_currency} balance for {side} {pair}")
                return False

            asset_amount = amount_in_usd / current_price

            # Deduct USD, add Asset
            self.balances[self.base_currency] -= amount_in_usd
            self.balances[asset] = self.balances.get(asset, 0) + asset_amount

            # Update avg entry price
            current_asset_holding = self.balances[asset]
            old_avg = self.avg_entry_prices.get(asset, 0)
            # Weighted average
            new_avg = ((current_asset_holding - asset_amount) * old_avg + asset_amount * current_price) / current_asset_holding
            self.avg_entry_prices[asset] = new_avg

            trade = TradeInfo(datetime.datetime.now().timestamp(), pair, side, asset_amount, current_price, amount_in_usd)
            self.trades.append(trade)
            print(f"Executed {side} {asset_amount:.6f} {asset} @ {current_price:.2f} {quote} (Total: {amount_in_usd:.2f})")
            return True

        elif side == 'SELL':
            asset_amount = self.balances.get(asset, 0)
            if asset_amount <= 0:
                print(f"No {asset} balance to {side}")
                return False

            usd_value = asset_amount * current_price

            # Deduct Asset, add USD
            self.balances[asset] -= asset_amount
            self.balances[self.base_currency] += usd_value

            # Clear average entry price since we sold everything
            if self.balances[asset] < 1e-8: # floating point 0 check
                self.balances[asset] = 0
                self.avg_entry_prices[asset] = 0

            trade = TradeInfo(datetime.datetime.now().timestamp(), pair, side, asset_amount, current_price, usd_value)
            self.trades.append(trade)
            print(f"Executed {side} {asset_amount:.6f} {asset} @ {current_price:.2f} {quote} (Total: {usd_value:.2f})")
            return True

        return False

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """
        Calculate total portfolio value based on latest market prices.
        current_prices format: {'BTC': 60000.0, 'ETH': 3000.0, ...}
        """
        total_value = self.balances.get(self.base_currency, 0)
        asset_values = {}

        for asset, amount in self.balances.items():
            if asset == self.base_currency or amount <= 0:
                continue

            price = current_prices.get(asset, 0)
            value = amount * price
            asset_values[asset] = {
                "amount": amount,
                "price": price,
                "value": value,
                "avg_entry": self.avg_entry_prices.get(asset, 0),
                "pnl_pct": ((price - self.avg_entry_prices.get(asset, 0)) / self.avg_entry_prices.get(asset, 1)) * 100 if self.avg_entry_prices.get(asset, 0) > 0 else 0
            }
            total_value += value

        return {
            "total_value_usd": total_value,
            "cash_usd": self.balances.get(self.base_currency, 0),
            "assets": asset_values,
            "total_pnl_usd": total_value - self.initial_balance,
            "total_pnl_pct": ((total_value - self.initial_balance) / self.initial_balance) * 100
        }

    def get_trade_history(self) -> List[Dict]:
        return [trade.to_dict() for trade in reversed(self.trades)] # Newest first

if __name__ == "__main__":
    engine = PaperTradingEngine(100.0)
    print("Initial Balance:", engine.get_balance())

    # Simulate Buy BTC
    engine.execute_trade('BTC_USDT', 'BUY', 65000.0, amount_in_usd=25.0)
    # Simulate Buy ETH
    engine.execute_trade('ETH_USDT', 'BUY', 2000.0, amount_in_usd=25.0)

    print("\nBalance after buys:", engine.get_balance())

    # Simulate price changes
    prices = {'BTC': 66000.0, 'ETH': 1900.0}
    print("\nPortfolio Value:", json.dumps(engine.get_portfolio_value(prices), indent=2))

    # Simulate Sell BTC
    engine.execute_trade('BTC_USDT', 'SELL', 66000.0)

    print("\nFinal Portfolio Value:", json.dumps(engine.get_portfolio_value(prices), indent=2))
    print("\nTrade History:")
    print(json.dumps(engine.get_trade_history(), indent=2))
