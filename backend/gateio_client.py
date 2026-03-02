import requests
import pandas as pd
import asyncio
import aiohttp
from typing import List, Dict, Optional

class GateIOClient:
    def __init__(self):
        self.base_url = "https://api.gateio.ws/api/v4"
        self.spot_url = f"{self.base_url}/spot"

    def get_ticker(self, currency_pair: str) -> Optional[Dict]:
        """Fetch the current ticker information for a currency pair."""
        url = f"{self.spot_url}/tickers"
        params = {"currency_pair": currency_pair}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                return data[0]
        return None

    def get_candlesticks(self, currency_pair: str, interval: str = "1m", limit: int = 100) -> pd.DataFrame:
        """
        Fetch historical candlestick data and return it as a pandas DataFrame.
        Gate.io returns: [timestamp, volume, close, high, low, open, ...]
        """
        url = f"{self.spot_url}/candlesticks"
        params = {
            "currency_pair": currency_pair,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Gate.io returns list of lists.
            # Index format: 0: unix_timestamp, 1: volume (quote), 2: close, 3: high, 4: low, 5: open, 6: volume (base), 7: window flag
            df = pd.DataFrame(data, columns=["timestamp", "quote_volume", "close", "high", "low", "open", "base_volume", "window_flag"])

            # Convert types
            for col in ["quote_volume", "close", "high", "low", "open", "base_volume"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit='s')
            df.sort_values("timestamp", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        return pd.DataFrame()

    async def get_multiple_tickers(self, currency_pairs: List[str]) -> Dict[str, Dict]:
        """Fetch multiple tickers concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for pair in currency_pairs:
                url = f"{self.spot_url}/tickers?currency_pair={pair}"
                tasks.append(self._fetch_async(session, url, pair))

            results = await asyncio.gather(*tasks)

            output = {}
            for pair, data in results:
                if data and len(data) > 0:
                    output[pair] = data[0]
            return output

    async def _fetch_async(self, session: aiohttp.ClientSession, url: str, pair: str):
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return pair, data
            return pair, None

if __name__ == "__main__":
    client = GateIOClient()
    print("Testing get_ticker BTC_USDT:")
    print(client.get_ticker("BTC_USDT"))

    print("\nTesting get_candlesticks ETH_USDT:")
    df = client.get_candlesticks("ETH_USDT", limit=5)
    print(df)

    print("\nTesting get_multiple_tickers:")
    pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
    results = asyncio.run(client.get_multiple_tickers(pairs))
    print(results)
