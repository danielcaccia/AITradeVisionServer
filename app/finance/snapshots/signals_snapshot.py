import yfinance as yf
import pandas_ta as ta

from datetime import datetime

from app.persistence.models import TechnicalSignal

from app.finance.tickers_list import TICKERS

class SignalSnapshot:
    def __init__(self):
        pass

    def detect_signals(self):
        print("Updating signals data...")
        print("============================================")

        TechnicalSignal.delete().where(TechnicalSignal.created_at < datetime.now().date()).execute()

        for ticker in TICKERS:
            df = yf.download(ticker, period="3mo", interval="1d")
            ticker = yf.Ticker(ticker)

            name = ticker.info.get("shortName", ticker)

            if df.empty:
                continue

            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            signal_summary = []
            macd_cross_type = None

            # RSI conditions
            if latest["RSI_14"] > 70:
                signal_summary.append("Overbought RSI")
            elif latest["RSI_14"] < 30:
                signal_summary.append("Oversold RSI")

            # MACD cross
            if prev["MACD_12_26_9"] < prev["MACDs_12_26_9"] and latest["MACD_12_26_9"] > latest["MACDs_12_26_9"]:
                signal_summary.append("MACD line crossing above the signal line")
                macd_cross_type = "bullish"
            elif prev["MACD_12_26_9"] > prev["MACDs_12_26_9"] and latest["MACD_12_26_9"] < latest["MACDs_12_26_9"]:
                signal_summary.append("MACD line crossing below the signal line")
                macd_cross_type = "bearish"

            if signal_summary:
                TechnicalSignal.create(
                    symbol=ticker,
                    name=name,
                    last_price=latest["Close"],
                    rsi=latest["RSI_14"],
                    macd_cross=macd_cross_type,
                    signal_summary=", ".join(signal_summary),
                    created_at=datetime.now()
                )

        print("============================================")
        print("Signals data updated.")

    def detect_signalsForDevEnv(self):
        print("Running in DEV MODE: Updating signals data...")
        print("============================================")

        TechnicalSignal.delete().where(TechnicalSignal.created_at < datetime.now().date()).execute()

        for ticker in ['AAPL', 'DIS', 'TSLA', 'VZ']:
            df = yf.download(ticker, period="3mo", interval="1d")
            ticker = yf.Ticker(ticker)

            name = ticker.info.get("shortName", ticker)

            if df.empty:
                continue
            
            df.columns = df.columns.to_flat_index()
            df.columns = [col if isinstance(col, str) else col[0] for col in df.columns]

            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            signal_summary = []
            macd_cross_type = None

            # RSI conditions
            if latest["RSI_14"] > 70:
                signal_summary.append("Overbought RSI")
            elif latest["RSI_14"] < 30:
                signal_summary.append("Oversold RSI")

            # MACD cross
            if prev["MACD_12_26_9"] < prev["MACDs_12_26_9"] and latest["MACD_12_26_9"] > latest["MACDs_12_26_9"]:
                signal_summary.append("MACD line crossing above the signal line")
                macd_cross_type = "bullish"
            elif prev["MACD_12_26_9"] > prev["MACDs_12_26_9"] and latest["MACD_12_26_9"] < latest["MACDs_12_26_9"]:
                signal_summary.append("MACD line crossing below the signal line")
                macd_cross_type = "bearish"

            if signal_summary:
                TechnicalSignal.create(
                    symbol=ticker,
                    name=name,
                    last_price=latest["Close"],
                    rsi=latest["RSI_14"],
                    macd_cross=macd_cross_type,
                    signal_summary=", ".join(signal_summary),
                    created_at=datetime.now()
                )

        print("============================================")
        print("Signals data updated.")
