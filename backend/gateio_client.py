import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Any

class GateIOClient:
    def __init__(self):
        self.base_url = "https://api.gateio.ws/api/v4"
        self.spot_url = f"{self.base_url}/spot"

    def _fetch_json(self, url: str) -> Optional[Any]:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    body = response.read()
                    return json.loads(body)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def get_ticker(self, currency_pair: str) -> Optional[Dict]:
        """Fetch the current ticker information for a currency pair."""
        url = f"{self.spot_url}/tickers?currency_pair={currency_pair}"
        data = self._fetch_json(url)
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_candlesticks(self, currency_pair: str, interval: str = "1m", limit: int = 100) -> List[Dict]:
        """
        Fetch historical candlestick data and return it as a list of dicts.
        Gate.io returns list of lists:
        Index format: 0: unix_timestamp, 1: volume (quote), 2: close, 3: high, 4: low, 5: open, 6: volume (base), 7: window flag
        """
        url = f"{self.spot_url}/candlesticks?currency_pair={currency_pair}&interval={interval}&limit={limit}"
        data = self._fetch_json(url)
        if data and isinstance(data, list):
            # Sort chronologically (oldest first)
            data.sort(key=lambda x: int(x[0]))

            records = []
            for row in data:
                try:
                    records.append({
                        "timestamp": int(row[0]),
                        "quote_volume": float(row[1]),
                        "close": float(row[2]),
                        "high": float(row[3]),
                        "low": float(row[4]),
                        "open": float(row[5]),
                        "base_volume": float(row[6])
                    })
                except (ValueError, IndexError):
                    continue
            return records
        return []

    def get_multiple_tickers(self, currency_pairs: List[str]) -> Dict[str, Dict]:
        """Fetch multiple tickers (sync fallback)."""
        import threading
        output = {}

        def fetch_worker(pair):
            res = self.get_ticker(pair)
            if res:
                output[pair] = res

        threads = []
        for pair in currency_pairs:
            t = threading.Thread(target=fetch_worker, args=(pair,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return output

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
