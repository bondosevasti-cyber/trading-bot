import requests

def get_btc_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # წყარო 1: Binance API (არ ბლოკავს Render-ს)
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return float(res.json()['price'])
    except Exception as e:
        print(f"❌ Error details (Binance): {e}")

    # წყარო 2: CoinGecko API (სარეზერვო, უსასყიდლო)
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return float(res.json()['bitcoin']['usd'])
    except Exception as e:
        print(f"❌ Error details (CoinGecko): {e}")

    # წყარო 3: CryptoCompare API (სარეზერვო)
    try:
        url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return float(res.json()['USD'])
    except Exception as e:
        print(f"❌ Error details (CryptoCompare): {e}")

    return None

if __name__ == '__main__':
    price = get_btc_price()
    print(f"📈 BTC ფასი: ${price}")