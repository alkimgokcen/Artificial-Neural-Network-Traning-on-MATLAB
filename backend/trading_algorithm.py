from typing import List, Dict

class TradingAlgorithm:
    def __init__(self, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9, bb_period=20, bb_std=2, interval="1m", leverage=1.0, take_profit=0.05, stop_loss=0.02):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.interval = interval
        self.leverage = leverage
        self.take_profit = take_profit
        self.stop_loss = stop_loss

    def update_params(self, params: dict):
        if 'rsi_period' in params: self.rsi_period = int(params['rsi_period'])
        if 'macd_fast' in params: self.macd_fast = int(params['macd_fast'])
        if 'macd_slow' in params: self.macd_slow = int(params['macd_slow'])
        if 'macd_signal' in params: self.macd_signal = int(params['macd_signal'])
        if 'bb_period' in params: self.bb_period = int(params['bb_period'])
        if 'bb_std' in params: self.bb_std = float(params['bb_std'])
        if 'interval' in params: self.interval = str(params['interval'])
        if 'leverage' in params: self.leverage = float(params['leverage'])
        if 'take_profit' in params: self.take_profit = float(params['take_profit'])
        if 'stop_loss' in params: self.stop_loss = float(params['stop_loss'])

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average."""
        if not prices: return []
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period] if len(prices) >= period else [prices[0]]

        # We need an array of the same length to map it back, pad initial with None
        result = [None] * (period - 1) + [ema[0]]
        for price in prices[period:]:
            new_ema = (price - ema[-1]) * multiplier + ema[-1]
            ema.append(new_ema)
            result.append(new_ema)
        return result

    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average."""
        result = [None] * len(prices)
        for i in range(period - 1, len(prices)):
            result[i] = sum(prices[i - period + 1 : i + 1]) / period
        return result

    def calculate_std(self, prices: List[float], period: int) -> List[float]:
        """Calculate Standard Deviation for a rolling window."""
        import math
        result = [None] * len(prices)
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1 : i + 1]
            mean = sum(window) / period
            variance = sum((x - mean) ** 2 for x in window) / period
            result[i] = math.sqrt(variance)
        return result

    def add_indicators(self, data: List[Dict]) -> List[Dict]:
        """Calculates RSI, MACD, and Bollinger Bands using pure Python math."""
        if len(data) < max(self.macd_slow, self.rsi_period, self.bb_period):
            return data

        prices = [d['close'] for d in data]
        n = len(prices)

        # 1. RSI
        gains = [0.0] * n
        losses = [0.0] * n
        for i in range(1, n):
            change = prices[i] - prices[i-1]
            if change > 0: gains[i] = change
            else: losses[i] = abs(change)

        rsi_values = [None] * n
        avg_gain = sum(gains[1:self.rsi_period+1]) / self.rsi_period
        avg_loss = sum(losses[1:self.rsi_period+1]) / self.rsi_period

        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss

        rsi_values[self.rsi_period] = 100 - (100 / (1 + rs))

        for i in range(self.rsi_period + 1, n):
            avg_gain = ((avg_gain * (self.rsi_period - 1)) + gains[i]) / self.rsi_period
            avg_loss = ((avg_loss * (self.rsi_period - 1)) + losses[i]) / self.rsi_period
            if avg_loss == 0:
                rsi_values[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi_values[i] = 100 - (100 / (1 + rs))

        # 2. MACD
        ema_fast = self.calculate_ema(prices, self.macd_fast)
        ema_slow = self.calculate_ema(prices, self.macd_slow)
        macd_line = [None] * n

        for i in range(n):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line[i] = ema_fast[i] - ema_slow[i]

        # Signal line is EMA of MACD
        # Find first valid macd value
        first_valid_macd_idx = next((i for i, v in enumerate(macd_line) if v is not None), -1)

        macd_signal = [None] * n
        if first_valid_macd_idx != -1 and first_valid_macd_idx + self.macd_signal <= n:
            valid_macd_subset = macd_line[first_valid_macd_idx:]
            signal_subset = self.calculate_ema(valid_macd_subset, self.macd_signal)
            macd_signal[first_valid_macd_idx:] = signal_subset

        macd_diff = [None] * n
        for i in range(n):
            if macd_line[i] is not None and macd_signal[i] is not None:
                macd_diff[i] = macd_line[i] - macd_signal[i]

        # 3. Bollinger Bands
        sma = self.calculate_sma(prices, self.bb_period)
        std_dev = self.calculate_std(prices, self.bb_period)

        bb_high = [None] * n
        bb_low = [None] * n

        for i in range(n):
            if sma[i] is not None and std_dev[i] is not None:
                bb_high[i] = sma[i] + (std_dev[i] * self.bb_std)
                bb_low[i] = sma[i] - (std_dev[i] * self.bb_std)

        # Map back to data objects
        for i in range(n):
            data[i]['rsi'] = rsi_values[i]
            data[i]['macd'] = macd_line[i]
            data[i]['macd_signal'] = macd_signal[i]
            data[i]['macd_diff'] = macd_diff[i]
            data[i]['bb_high'] = bb_high[i]
            data[i]['bb_low'] = bb_low[i]
            data[i]['bb_mid'] = sma[i]

        return data

    def evaluate(self, data: List[Dict]) -> str:
        """
        Evaluates the data with indicators and returns a signal:
        'BUY', 'SELL', or 'HOLD'.
        """
        if not data or len(data) < 2:
            return 'HOLD'

        latest = data[-1]
        previous = data[-2]

        # Don't trade if indicators are still missing
        if latest.get('rsi') is None or latest.get('macd') is None or latest.get('bb_high') is None:
            return 'HOLD'

        # LONG Signal Conditions (Bullish)
        # 1. RSI is oversold (< 30) or recovering from oversold (previous < 30, latest > 30)
        # 2. MACD crosses above Signal Line
        # 3. Price touches or crosses below lower Bollinger Band

        buy_condition_rsi = latest['rsi'] < 40  # Less strict for demo purposes
        buy_condition_macd = latest['macd'] > latest['macd_signal'] and previous['macd'] <= previous['macd_signal']
        buy_condition_bb = latest['close'] <= latest['bb_low'] * 1.01  # Price is near or below lower band

        # We need at least 2 out of 3 signals to align for a strong buy
        buy_signals = sum([buy_condition_rsi, buy_condition_macd, buy_condition_bb])
        if buy_signals >= 2:
            return 'LONG'

        # SHORT Signal Conditions (Bearish)
        # 1. RSI is overbought (> 70)
        # 2. MACD crosses below Signal Line
        # 3. Price touches or crosses above upper Bollinger Band

        sell_condition_rsi = latest['rsi'] > 60  # Less strict for demo purposes
        sell_condition_macd = latest['macd'] < latest['macd_signal'] and previous['macd'] >= previous['macd_signal']
        sell_condition_bb = latest['close'] >= latest['bb_high'] * 0.99  # Price is near or above upper band

        sell_signals = sum([sell_condition_rsi, sell_condition_macd, sell_condition_bb])
        if sell_signals >= 2:
            return 'SHORT'

        return 'HOLD'

if __name__ == "__main__":
    from gateio_client import GateIOClient
    import time

    client = GateIOClient()
    algo = TradingAlgorithm()

    print("Testing algorithm with historical ETH data...")
    # Fetch enough data to calculate all indicators
    df = client.get_candlesticks("ETH_USDT", limit=100)
    df_with_indicators = algo.add_indicators(df)

    print(df_with_indicators[['timestamp', 'close', 'rsi', 'macd_diff', 'bb_low', 'bb_high']].tail())

    signal = algo.evaluate(df_with_indicators)
    print(f"\nResulting Signal: {signal}")
