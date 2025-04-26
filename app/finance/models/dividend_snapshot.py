import requests
import traceback

from datetime import datetime, timedelta

from ..clients.fmp_client import fmp_get, fmp_get_dev_env
from ..persistence.models import Dividend
from ..tickers_list import TICKERS

class DividendSnapshot:
    def __init__(self):
        pass

    def update_upcoming_dividends(self, days_ahead=60):
        print("Updating dividend data...")
        print("============================================")

        now = datetime.now()
        limit_date = now + timedelta(days=days_ahead)

        Dividend.delete().where(Dividend.ex_dividend_date >= now.date()).execute()

        for symbol in TICKERS:
            print(f"Fetching dividend for symbol: {symbol}")

            try:
                data = fmp_get(f"stock_dividend_calendar", params={"symbol": symbol})
                
                if not data:
                    print(f"No dividend data for {symbol}")
                    continue

                for item in data:
                    ex_dividend_date = datetime.strptime(item["date"], "%Y-%m-%d").date()

                    if now.date() <= ex_dividend_date <= limit_date.date():
                        Dividend.create(
                            symbol=symbol,
                            name=item.get("companyName", symbol),
                            ex_dividend_date=ex_dividend_date,
                            dividend_per_share=float(item.get("dividend", 0)),
                            payment_date=None,
                            record_date=None,
                            declaration_date=None,
                            created_at=datetime.now()
                        )

                        print(f"Dividend saved: {symbol} - {ex_dividend_date}")

            except Exception as e:
                print(traceback.format_exc())
                print(f"Error on {symbol}: {e}")

        print("============================================")
        print("Dividend data updated.")

    def update_upcoming_dividendsForDevEnv(self, days_ahead=60):
        print("Running in DEV MODE: Fetching general dividend calendar...")

        now = datetime.now()
        limit_date = now + timedelta(days=days_ahead)

        Dividend.delete().where(Dividend.ex_dividend_date >= now.date()).execute()

        try:
            data = fmp_get_dev_env("dividends-calendar")

            if not data:
                print("No dividend data found.")
                return

            for item in data[:5]:  
                ex_dividend_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
                symbol = item["symbol"]

                Dividend.create(
                    symbol=symbol,
                    name=item.get("companyName", symbol),
                    ex_dividend_date=ex_dividend_date,
                    dividend_per_share=float(item.get("dividend", 0)),
                    payment_date=None,
                    record_date=None,
                    declaration_date=None,
                    created_at=datetime.now()
                )
                print(f"Dividend saved: {symbol} - {ex_dividend_date}")

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error in DEV MODE: {e}")

        print("============================================")
        print("Dividend data updated.")