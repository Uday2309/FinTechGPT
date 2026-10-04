import yfinance as yf


def get_stock_quote(symbol: str):
    ticker = symbol.upper().strip()
    # Indian NSE tickers normally use .NS on Yahoo Finance.
    candidates = [ticker] if ticker.endswith((".NS", ".BO")) else [f"{ticker}.NS", ticker]
    for candidate in candidates:
        try:
            hist = yf.Ticker(candidate).history(period="5d", interval="1d", auto_adjust=False)
            if hist.empty:
                continue
            latest = hist.iloc[-1]
            price = float(latest["Close"])
            return {"symbol": candidate, "price": price, "date": hist.index[-1].strftime("%Y-%m-%d"), "source": "Yahoo Finance via yfinance"}
        except Exception:
            continue
    return {"symbol": ticker, "price": None, "date": None, "source": "Yahoo Finance via yfinance", "error": "Quote unavailable"}
