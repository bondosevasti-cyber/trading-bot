import requests

def get_btc_price():
    try:
        # Binance-ის საჯარო API (არ ბლოკავს Render-ის სერვერებს)
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return float(data['price'])
    except Exception as e:
        print(f"⚠️ ფასის წამოღების შეცდომა: {e}")
        return None

if __name__ == '__main__':
    price = get_btc_price()
    print(f"📈 BTC ფასი: ${price}")