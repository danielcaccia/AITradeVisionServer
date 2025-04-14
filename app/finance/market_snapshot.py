import yfinance as yf
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from finance.tickers_list import TICKERS

market_cache = {
    "gainers": [],
    "losers": [],
    "trending": []
}

def update_market_data():
    print("Updating market data...")
    print("============================================")

    data = []
    
    for symbol in TICKERS:
        print(f"Fetching symbol: {symbol}")
        print("--------------------------------------------")

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
            print(f"Error fetching symbol: {symbol}: {e}")
    
    # Order data
    sorted_by_variation = sorted(data, key=lambda x: x["variation"], reverse=True)
    sorted_by_volume_spike = sorted(data, key=lambda x: x["volume_spike"], reverse=True)

    # Feed the cache memory with updated data
    market_cache["gainers"] = sorted_by_variation[:5]
    market_cache["losers"] = sorted_by_variation[-5:]
    market_cache["trending"] = sorted_by_volume_spike[:5]

    print("============================================")
    print("Market data updated.")

def start_market_snapshot_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_market_data, "interval", hours=1)
    scheduler.start()

    update_market_data()