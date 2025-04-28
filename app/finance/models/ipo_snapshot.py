import traceback

from datetime import datetime, timedelta

from ..clients.fmp_client import fmp_get, fmp_get_dev_env
from ..persistence.models import Ipo

class IPOSnapshot:
    def __init__(self):
        pass

    def update_upcoming_ipos(self, days_ahead=60):
        print("Updating IPO data...")
        print("============================================")

        now = datetime.now()
        limit_date = now + timedelta(days=days_ahead)

        Ipo.delete().where(Ipo.ipo_date >= now.date()).execute()

        try:
            data = fmp_get("ipo_calendar")
            
            if not data:
                print("No IPO data found.")
                return

            for item in data:
                ipo_date = datetime.strptime(item["date"], "%Y-%m-%d").date()

                if now.date() <= ipo_date <= limit_date.date():
                    Ipo.create(
                        symbol=item["symbol"],
                        name=item.get("company"),
                        exchange=item.get("exchange", ""),
                        ipo_date=ipo_date,
                        price_range=item.get("priceRange", None),
                        created_at=datetime.now()
                    )

                    print(f"IPO saved: {item['symbol']} - {ipo_date}")

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error fetching IPOs: {e}")

        print("============================================")
        print("IPO data updated.")

    def update_upcoming_iposForDevEnv(self, days_ahead=60):
        print("Running in DEV MODE: Fetching general IPO calendar...")

        now = datetime.now()

        Ipo.delete().where(Ipo.ipo_date >= now.date()).execute()

        try:
            data = [
                    {
                        "symbol": "TEST1",
                        "name": "Mock Company 1",
                        "exchange": "Doe Johnes",
                        "date": "2025-05-10",
                        "priceRange": 20.00
                    },
                    {
                        "symbol": "TEST2",
                        "name": "Mock Company 2",
                        "exchange": "Doe Johnes",
                        "date": "2025-05-12",
                        "priceRange": 15.00
                    }
                ]

            for item in data[:5]:  
                Ipo.create(
                    symbol=item["symbol"],
                    name=item.get("name", item["symbol"]),
                    exchange=item.get("exchange", ""),
                    ipo_date=datetime.strptime(item.get("date"), "%Y-%m-%d").date(),
                    price_range=item.get("priceRange", None),
                    created_at=datetime.now()
                )

                print(f"IPO saved: {item['symbol']} - {item.get("date")}")

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error in DEV MODE IPOs: {e}")

        print("============================================")
        print("IPO data updated.")