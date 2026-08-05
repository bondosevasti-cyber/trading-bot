import requests

def get_btc_price():
    try:
        # Bybit-ის საჯარო მისამართი ფასების მისაღებად
        url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # პასუხიდან ამოვიღებთ ბიტკოინის ბოლო ფასს
        price = float(data['result']['list'][0]['lastPrice'])
        return price
    except Exception as e:
        print(f"⚠️ ფასის წამოღების შეცდომა: {e}")
        return None

# შევამოწმოთ მუშაობს თუ არა:
if __name__ == '__main__':
    current_price = get_btc_price()
    if current_price:
        print(f"📈 ბიტკოინის რეალური ფასი Bybit-ზე: ${current_price}")
    else:
        print("❌ ფასის წამოღება ვერ მოხერხდა")