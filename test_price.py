import yfinance as yf

t = yf.Ticker('HDFCBANK.NS')
info = t.info
print(f"currentPrice: {info.get('currentPrice')}")
print(f"regularMarketPrice: {info.get('regularMarketPrice')}")
print(f"previousClose: {info.get('previousClose')}")
print(f"dayHigh: {info.get('dayHigh')}")
print(f"dayLow: {info.get('dayLow')}")
print()
hist = t.history(period='5d')
print("Last 5 days close:")
print(hist[['Close']].tail())
