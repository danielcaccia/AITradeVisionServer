import yfinance as yf

class StockQuote:
    def __init__(self):
        pass

    def get_quote(self, symbol):
        try:
            symbol = symbol.upper()
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")

            if data.empty:
                return {"error": "Invalid stock symbol or no data available."}

            latest_quote = data.iloc[-1]
            return {
                "symbol": symbol,
                "date": str(latest_quote.name.date()),
                "open": latest_quote["Open"],
                "high": latest_quote["High"],
                "low": latest_quote["Low"],
                "close": latest_quote["Close"],
                "volume": latest_quote["Volume"]
            }

        except Exception as e:
            return {"error": str(e)}

    def get_history(self, symbol, period="6mo"):
        try:
            symbol = symbol.upper()
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)

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

            return {"symbol": symbol, "history": history}

        except Exception as e:
            return {"error": str(e)}