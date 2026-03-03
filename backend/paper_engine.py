import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger("TradingEngine")

class TradeInfo:
    def __init__(self, timestamp: float, pair: str, side: str, amount: float, price: float, total: float, leverage: float = 1.0, position_type: str = "SPOT"):
        self.timestamp = timestamp
        self.pair = pair
        self.side = side # 'BUY' or 'SELL'
        self.amount = amount
        self.price = price
        self.total = total # In USDT
        self.leverage = leverage
        self.position_type = position_type # "LONG" or "SHORT" or "SPOT"

    def to_dict(self):
        return {
            "timestamp": datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "pair": self.pair,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
            "total": self.total,
            "leverage": self.leverage,
            "position_type": self.position_type
        }

class Position:
    def __init__(self, pair: str, position_type: str, amount: float, entry_price: float, leverage: float, margin_used: float):
        self.pair = pair
        self.position_type = position_type # 'LONG' or 'SHORT'
        self.amount = amount # Size in asset (e.g. 0.5 BTC)
        self.entry_price = entry_price
        self.leverage = leverage
        self.margin_used = margin_used # Initial collateral locked for this position in USDT

    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate Unrealized PnL based on position type."""
        if self.position_type == 'LONG':
            # Buy low, sell high
            return (current_price - self.entry_price) * self.amount
        elif self.position_type == 'SHORT':
            # Sell high, buy low
            return (self.entry_price - current_price) * self.amount
        return 0.0

    def get_liquidation_price(self) -> float:
        """
        Estimate liquidation price.
        Maintenance Margin is usually around 0.5% - 1% of position value, but for simplicity,
        we liquidate when margin is depleted by 95% (to cover fees/slippage).
        """
        margin_threshold = self.margin_used * 0.05

        if self.position_type == 'LONG':
            # Loss = (entry - current) * amount
            # When Loss >= margin_used - margin_threshold, liquidate.
            # (entry - Liq) * amount = margin_used * 0.95
            return self.entry_price - ((self.margin_used * 0.95) / self.amount)
        elif self.position_type == 'SHORT':
            # Loss = (current - entry) * amount
            return self.entry_price + ((self.margin_used * 0.95) / self.amount)
        return 0.0


class PaperTradingEngine:
    def __init__(self, initial_balance: float = 100.0, base_currency: str = "USDT"):
        self.base_currency = base_currency
        self.initial_balance = initial_balance
        self.available_cash = initial_balance

        # Keep track of active margin positions
        self.positions: Dict[str, Position] = {} # pair -> Position object
        self.trades: List[TradeInfo] = []

    def get_balance(self) -> Dict[str, float]:
        """Return available cash and active margin locks."""
        return {
            self.base_currency: self.available_cash,
            "locked_margin": sum(p.margin_used for p in self.positions.values())
        }

    def close_position(self, pair: str, current_price: float, reason: str = "MANUAL") -> bool:
        """Close an open position (either Long or Short) completely."""
        if pair not in self.positions:
            return False

        pos = self.positions[pair]
        pnl = pos.get_unrealized_pnl(current_price)

        # Return initial margin + PnL back to available cash
        returned_cash = pos.margin_used + pnl

        # Prevent negative balance, min is 0 if liquidated fully
        if returned_cash < 0:
            returned_cash = 0

        self.available_cash += returned_cash

        side = 'SELL' if pos.position_type == 'LONG' else 'BUY' # To close long, you sell. To close short, you buy.
        total_value = pos.amount * current_price

        trade = TradeInfo(datetime.datetime.now().timestamp(), pair, f"{side}_CLOSE", pos.amount, current_price, total_value, pos.leverage, pos.position_type)
        self.trades.append(trade)

        logger.info(f"Closed {pos.position_type} on {pair} at {current_price}. PnL: {pnl:.2f}. Reason: {reason}")
        del self.positions[pair]
        return True

    def open_position(self, pair: str, position_type: str, current_price: float, margin_amount: float, leverage: float = 1.0) -> bool:
        """Open a new margin LONG or SHORT position."""
        if pair in self.positions:
            logger.warning(f"Position for {pair} already exists. Close it first.")
            return False # For simplicity, 1 active position per pair at a time

        if self.available_cash < margin_amount:
            logger.warning(f"Insufficient funds. Need {margin_amount}, have {self.available_cash}")
            return False

        # Deduct margin from available cash
        self.available_cash -= margin_amount

        # Calculate actual trade size
        leveraged_value = margin_amount * leverage
        asset_amount = leveraged_value / current_price

        # Create position
        pos = Position(pair, position_type, asset_amount, current_price, leverage, margin_amount)
        self.positions[pair] = pos

        side = 'BUY' if position_type == 'LONG' else 'SELL'
        trade = TradeInfo(datetime.datetime.now().timestamp(), pair, f"{side}_OPEN", asset_amount, current_price, leveraged_value, leverage, position_type)
        self.trades.append(trade)

        logger.info(f"Opened {position_type} on {pair} at {current_price}. Margin: {margin_amount}, Lev: {leverage}x, Size: {asset_amount:.6f}")
        return True

    def check_liquidations_and_limits(self, current_prices: Dict[str, float], stop_loss_pct: float, take_profit_pct: float):
        """Iterate positions and close them if they hit liquidation, SL, or TP."""
        pairs_to_close = []
        for pair, pos in self.positions.items():
            asset = pair.split('_')[0]
            price = current_prices.get(asset)
            if not price:
                continue

            liq_price = pos.get_liquidation_price()
            unrealized_pnl = pos.get_unrealized_pnl(price)
            pnl_pct = unrealized_pnl / pos.margin_used # relative to initial margin

            # 1. Liquidation Check
            if (pos.position_type == 'LONG' and price <= liq_price) or \
               (pos.position_type == 'SHORT' and price >= liq_price):
                pairs_to_close.append((pair, "LIQUIDATION"))

            # 2. Stop Loss Check
            elif pnl_pct <= -stop_loss_pct:
                pairs_to_close.append((pair, "STOP_LOSS"))

            # 3. Take Profit Check
            elif pnl_pct >= take_profit_pct:
                pairs_to_close.append((pair, "TAKE_PROFIT"))

        # Close them
        for pair, reason in pairs_to_close:
            asset = pair.split('_')[0]
            self.close_position(pair, current_prices[asset], reason=reason)

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate total portfolio value including unrealized PnL."""
        total_unrealized_pnl = 0.0
        locked_margin = 0.0
        assets = {}

        for pair, pos in self.positions.items():
            asset = pair.split('_')[0]
            price = current_prices.get(asset, pos.entry_price) # fallback to entry if missing

            pnl = pos.get_unrealized_pnl(price)
            total_unrealized_pnl += pnl
            locked_margin += pos.margin_used

            assets[asset] = {
                "type": pos.position_type,
                "amount": pos.amount,
                "entry_price": pos.entry_price,
                "current_price": price,
                "leverage": pos.leverage,
                "margin_used": pos.margin_used,
                "unrealized_pnl": pnl,
                "pnl_pct": (pnl / pos.margin_used) * 100 if pos.margin_used > 0 else 0,
                "liquidation_price": pos.get_liquidation_price()
            }

        total_value = self.available_cash + locked_margin + total_unrealized_pnl

        return {
            "total_value_usd": total_value,
            "cash_usd": self.available_cash,
            "locked_margin_usd": locked_margin,
            "assets": assets,
            "total_pnl_usd": total_value - self.initial_balance,
            "total_pnl_pct": ((total_value - self.initial_balance) / self.initial_balance) * 100
        }

    def get_trade_history(self) -> List[Dict]:
        return [trade.to_dict() for trade in reversed(self.trades)]
