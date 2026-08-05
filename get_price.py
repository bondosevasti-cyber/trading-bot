import requests

def get_btc_price():
    # Bybit-ის საჯარო მისამართი ფასების მისაღებად
    url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
    
    response = requests.get(url)
    data = response.json()
    
    # პასუხიდან ამოვიღებთ ბიტკოინის ბოლო ფასს
    price = float(data['result']['list'][0]['lastPrice'])
    return price

# შევამოწმოთ მუშაობს თუ არა:
current_price = get_btc_price()
print(f"📈 ბიტკოინის რეალური ფასი Bybit-ზე: ${current_price}")