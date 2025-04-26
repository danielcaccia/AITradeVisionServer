import traceback
import yfinance as yf

from datetime import datetime

from ..persistence.models import MarketMovers
from ..tickers_list import TICKERS

class MarketSnapshot:
    def __init__(self):
        pass

    def update_market_data(self):
        print("Updating market data...")
        print("============================================")

        data = []
        
        # for symbol in TICKERS:
        for symbol in ['AAPL', 'VZ']:
            print(f"Fetching symbol: {symbol}")

            try:
                # Fetch data
                ticker = yf.Ticker(symbol)
                fast_info = ticker.fast_info
                hist = ticker.history(period="10d")

                # Empty check
                if not fast_info or hist.empty:
                    print(f"'fast_info'/'hist' not available. Move on...")
                    print("--------------------------------------------")
                    continue

                # Fetch name
                name = ticker.info.get("shortName", symbol)

                # Fetch prices
                last_price = fast_info["last_price"]
                open_price = fast_info["open"]

                # Fetch volumes
                current_volume = fast_info["last_volume"]
                avg_volume = hist["Volume"].mean()

                # Calculate current variation
                variation = ((last_price - open_price) / open_price) * 100

                # Calculate market trend based on spike volume
                volume_spike = ((current_volume / avg_volume) - 1) * 100 if avg_volume else 0

                data.append({
                    "symbol": symbol,
                    "name": name,
                    "price": last_price,
                    "variation": variation,
                    "volume_spike": volume_spike,
                    "current_volume": current_volume,
                    "avg_volume": avg_volume
                })

                print(f"Symbol successfully obtained: {symbol}")
                print("--------------------------------------------")

            except Exception as e:
                print(traceback.format_exc())
                print(f"Error fetching symbol: {symbol}: {e}")
        
        # Order data
        sorted_by_variation = sorted(data, key=lambda x: x["variation"], reverse=True)
        sorted_by_volume_spike = sorted(data, key=lambda x: x["volume_spike"], reverse=True)

        now = datetime.now()
        MarketMovers.delete().execute()

        # Feed the database with updated data
        for i, record in enumerate(sorted_by_volume_spike[:5]):
            MarketMovers.create(**record, snapshot_type="trending", created_at=now)
        
        for i, record in enumerate(sorted_by_variation[:5]):
            MarketMovers.create(**record, snapshot_type="gainer", created_at=now)
        
        for i, record in enumerate(sorted_by_variation[-5:]):
            MarketMovers.create(**record, snapshot_type="loser", created_at=now)

        print("============================================")
        print("Market data updated.")
