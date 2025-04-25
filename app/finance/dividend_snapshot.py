import traceback
import yfinance as yf

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from finance.tickers_list import TICKERS

class DividendSnapshot:
    def __init__(self):
        self.upcoming_dividends = []

    def update_upcoming_dividends(self, days_ahead=14):
        print("Updating dividend data...")
        print("============================================")

        upcoming = []
        now = datetime.now()
        limit_date = now + timedelta(days=days_ahead)

        for symbol in TICKERS:
            print(f"Fetching dividend for symbol: {symbol}")

            try:
                stock = yf.Ticker(symbol)
                dividends = stock.dividends

                if not dividends.empty:
                    last_date = dividends.index[-1].replace(tzinfo=None)
                    if now <= last_date <= limit_date:
                        info = stock.info
                        upcoming.append({
                            "symbol": symbol,
                            "name": info.get("shortName", symbol),
                            "dividend_date": str(last_date.date()),
                            "last_dividend": dividends[-1],
                            "yield": info.get("dividendYield", 0)
                        })
                
                print(f"Dividend successfully obtained for: {symbol}")
                print("--------------------------------------------")

            except Exception as e:
                print(traceback.format_exc())
                print(f"Error on {symbol}: {e}")
        
        self.upcoming_dividends = sorted(upcoming, key=lambda x: x["dividend_date"])

        print("============================================")
        print("Dividend data updated.")

    def start_dividend_snapshot_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.update_upcoming_dividends, "interval", hours=24)
        scheduler.start()

        self.update_upcoming_dividends()