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
