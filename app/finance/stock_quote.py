import yfinance as yf

class StockQuote:
    def __init__(self):
        pass

    def get_quote(self, symbol):
        try:
            symbol = symbol.upper()
            stock = yf.Ticker(symbol)
            quote = stock.fast_info
            display_name = stock.info.get("displayName")

            if not quote:
                return {"error": "Invalid stock symbol or no data available."}

            variation = ((quote["last_price"] - quote["open"]) / quote["open"]) * 100

            return {
                "symbol": symbol,
                "display_name": display_name,
                "open": quote["open"],
                "day_high": quote["day_high"],
                "day_low": quote["day_low"],
                "latest_price": quote["last_price"],
                "latest_volume": quote["last_volume"],
                "variation": variation
            }

        except Exception as e:
            return {"error": str(e)}

    def get_history(self, symbol, period="6mo"):
        try:
            symbol = symbol.upper()
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            display_name = stock.info.get("displayName")

            if data.empty:
                return {"error": "Invalid stock symbol or no data available."}

            history = [
                {
                    "date": str(index.date()),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                }
                for index, row in data.iterrows()
            ]

            return {
                "symbol": symbol,
                "display_name": display_name,
                "history": history
            }

        except Exception as e:
            return {"error": str(e)}
        
    def get_index(self, symbol):
        try:
            symbol = symbol.upper()
            stock = yf.Ticker(symbol)
            quote = stock.fast_info
            display_name = stock.info.get("shortName")

            if not quote:
                return {"error": "Invalid stock symbol or no data available."}
            
            variation = ((quote["last_price"] - quote["open"]) / quote["open"]) * 100

            return {
                "symbol": symbol,
                "open": quote["open"],
                "day_high": quote["day_high"],
                "day_low": quote["day_low"],
                "latest_price": quote["last_price"],
                "latest_volume": quote["last_volume"],
                "variation": variation
            }

        except Exception as e:
            return {"error": str(e)}
