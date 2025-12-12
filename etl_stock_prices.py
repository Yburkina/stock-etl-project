import pandas as pd
import yfinance as yf
from datetime import date

TICKERS = ["AAPL", "MSFT", "AMD"]
PERIOD = "5y"   # change to "1y" if you want faster
INTERVAL = "1d"

def extract(tickers):
    df = yf.download(tickers, period=PERIOD, interval=INTERVAL, group_by="ticker", auto_adjust=False)
    return df

def transform(raw):
    # yfinance returns a multi-index if multiple tickers
    out = []
    if isinstance(raw.columns, pd.MultiIndex):
        for t in TICKERS:
            tdf = raw[t].copy()
            tdf["Ticker"] = t
            tdf = tdf.reset_index()  # Date becomes a column
            out.append(tdf)
        df = pd.concat(out, ignore_index=True)
    else:
        df = raw.reset_index()
        df["Ticker"] = TICKERS[0]

    # Clean column names
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # Basic cleaning: remove rows with missing Close
    if "Close" in df.columns:
        df = df.dropna(subset=["Close"])

    # Add a simple metric recruiters understand
    df["Daily_Return"] = df["Close"].pct_change()

    return df

def load(df):
    today = date.today().isoformat()
    csv_name = f"stock_prices_{today}.csv"
    xlsx_name = f"stock_prices_{today}.xlsx"

    df.to_csv(csv_name, index=False)
    df.to_excel(xlsx_name, index=False)

    print(f"Saved: {csv_name}")
    print(f"Saved: {xlsx_name}")

def main():
    raw = extract(TICKERS)
    cleaned = transform(raw)
    load(cleaned)

if __name__ == "__main__":
    main()
