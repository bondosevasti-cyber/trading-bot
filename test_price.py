import ccxt

# 1. ვუკავშირდებით Bybit ბირჟას საჯარო რეჟიმში
exchange = ccxt.bybit()

# 2. ვითხოვთ ბიტკოინის (BTC/USDT) მონაცემებს
ticker = exchange.fetch_ticker('BTC/USDT')

# 3. ვბეჭდავთ შედეგს ეკრანზე
print("=========================================")
print(f"ბიტკოინის ამჟამინდელი ფასია Bybit-ზე: {ticker['last']} USDT")
print("=========================================")