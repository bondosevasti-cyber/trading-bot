import requests

def get_btc_price():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    timeout = 10
    
    # 1. Bybit
    try:
        url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
        res = requests.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return float(res.json()['result']['list'][0]['lastPrice'])
    except Exception as e:
        print(f"❌ Bybit Error: {e}")

    # 2. Binance
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return float(res.json()['price'])
    except Exception as e:
        print(f"❌ Binance Error: {e}")

    # 3. Kraken
    try:
        url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
        res = requests.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return float(res.json()['result']['XXBTZUSD']['c'][0])
    except Exception as e:
        print(f"❌ Kraken Error: {e}")

    # 4. KuCoin
    try:
        url = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
        res = requests.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return float(res.json()['data']['price'])
    except Exception as e:
        print(f"❌ KuCoin Error: {e}")
        
    # 5. CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return float(res.json()['bitcoin']['usd'])
    except Exception as e:
        print(f"❌ CoinGecko Error: {e}")

    return None

if __name__ == '__main__':
    price = get_btc_price()
    print(f"📈 BTC ფასი: ${price}")