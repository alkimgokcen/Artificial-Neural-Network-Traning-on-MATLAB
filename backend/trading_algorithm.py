import pandas as pd
import ta

class TradingAlgorithm:
    def __init__(self, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9, bb_period=20, bb_std=2):
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std

    def update_params(self, params: dict):
        if 'rsi_period' in params: self.rsi_period = int(params['rsi_period'])
        if 'macd_fast' in params: self.macd_fast = int(params['macd_fast'])
        if 'macd_slow' in params: self.macd_slow = int(params['macd_slow'])
        if 'macd_signal' in params: self.macd_signal = int(params['macd_signal'])
        if 'bb_period' in params: self.bb_period = int(params['bb_period'])
        if 'bb_std' in params: self.bb_std = float(params['bb_std'])

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds RSI, MACD, and Bollinger Bands to the DataFrame."""
        if df.empty or len(df) < max(self.macd_slow, self.rsi_period, self.bb_period):
            return df

        # RSI
        rsi_indicator = ta.momentum.RSIIndicator(close=df['close'], window=self.rsi_period)
        df['rsi'] = rsi_indicator.rsi()

        # MACD
        macd_indicator = ta.trend.MACD(
            close=df['close'],
            window_slow=self.macd_slow,
            window_fast=self.macd_fast,
            window_sign=self.macd_signal
        )
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_diff'] = macd_indicator.macd_diff()

        # Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(
            close=df['close'],
            window=self.bb_period,
            window_dev=self.bb_std
        )
        df['bb_high'] = bb_indicator.bollinger_hband()
        df['bb_low'] = bb_indicator.bollinger_lband()
        df['bb_mid'] = bb_indicator.bollinger_mavg()

        return df

    def evaluate(self, df: pd.DataFrame) -> str:
        """
        Evaluates the DataFrame with indicators and returns a signal:
        'BUY', 'SELL', or 'HOLD'.
        """
        if df.empty or 'rsi' not in df.columns or len(df) < 2:
            return 'HOLD'

        # Get the latest row for decision
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Don't trade if indicators are still NaN
        if pd.isna(latest['rsi']) or pd.isna(latest['macd']) or pd.isna(latest['bb_high']):
            return 'HOLD'

        # Buy Signal Conditions
        # 1. RSI is oversold (< 30) or recovering from oversold (previous < 30, latest > 30)
        # 2. MACD crosses above Signal Line
        # 3. Price touches or crosses below lower Bollinger Band

        buy_condition_rsi = latest['rsi'] < 40  # Less strict for demo purposes
        buy_condition_macd = latest['macd'] > latest['macd_signal'] and previous['macd'] <= previous['macd_signal']
        buy_condition_bb = latest['close'] <= latest['bb_low'] * 1.01  # Price is near or below lower band

        # We need at least 2 out of 3 signals to align for a strong buy
        buy_signals = sum([buy_condition_rsi, buy_condition_macd, buy_condition_bb])
        if buy_signals >= 2:
            return 'BUY'

        # Sell Signal Conditions
        # 1. RSI is overbought (> 70)
        # 2. MACD crosses below Signal Line
        # 3. Price touches or crosses above upper Bollinger Band

        sell_condition_rsi = latest['rsi'] > 60  # Less strict for demo purposes
        sell_condition_macd = latest['macd'] < latest['macd_signal'] and previous['macd'] >= previous['macd_signal']
        sell_condition_bb = latest['close'] >= latest['bb_high'] * 0.99  # Price is near or above upper band

        sell_signals = sum([sell_condition_rsi, sell_condition_macd, sell_condition_bb])
        if sell_signals >= 2:
            return 'SELL'

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
