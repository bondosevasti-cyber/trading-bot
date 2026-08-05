import requests
import yfinance as yf

def get_price(symbol="BTCUSDT"):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    timeout = 10
    
    # Check if it's a known non-crypto ticker format for quick yfinance routing
    is_traditional = any(ext in symbol for ext in ["=X", "=F"]) or (len(symbol) <= 4 and not symbol.endswith("USDT"))
    
    if not is_traditional:
        # 1. Bybit
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
            res = requests.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                return float(res.json()['result']['list'][0]['lastPrice'])
        except Exception as e:
            pass # Suppress print to avoid log spam for traditional assets

        # 2. Binance
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            res = requests.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                return float(res.json()['price'])
        except Exception as e:
            pass

        # 3. KuCoin
        try:
            kucoin_symbol = symbol
            if symbol.endswith("USDT"):
                kucoin_symbol = symbol[:-4] + "-USDT"
            
            url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={kucoin_symbol}"
            res = requests.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                return float(res.json()['data']['price'])
        except Exception as e:
            pass

    # 4. yfinance (Fallback for traditional assets: AAPL, EURUSD=X, TSLA, GC=F)
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        if not history.empty:
            return float(history['Close'].iloc[-1])
    except Exception as e:
        print(f"❌ yfinance Error ({symbol}): {e}")
        
    return None

if __name__ == '__main__':
    for sym in ["BTCUSDT", "ETHUSDT", "AAPL", "EURUSD=X", "GC=F"]:
        p = get_price(sym)
        print(f"📈 {sym} ფასი: ${p}")