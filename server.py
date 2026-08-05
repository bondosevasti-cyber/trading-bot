from flask import Flask, request
from risk_manager import calculate_position
from get_price import get_btc_price  # 1. შემოვპორტოთ ფასის წამოღების ფუნქცია
from paper_trading import PaperTrader

app = Flask(__name__)
paper_trader = PaperTrader(initial_balance=110.0)

@app.route('/webhook', methods=['POST'])
def receive_signal():
    data = request.json or {}
    print("=========================================")
    print(f"🚨 მივიღეთ ახალი სიგნალი: {data}")
    
    # 2. ვიღებთ ბიტკოინის რეალურ ფასს ბირჟიდან
    current_price = get_btc_price()
    
    # 3. ვითვლით რისკებს რეალური ფასის მიხედვით
    qty, sl, tp = calculate_position(current_price)
    
    print(f"📈 მიმდინარე ფასი: ${current_price}")
    print(f"🪙 პოზიციის ზომა ($10-ის): {qty} BTC")
    print(f"🛑 Stop Loss: ${sl}")
    print(f"🎯 Take Profit: ${tp}")
    print("=========================================")
    
    # 4. ვასრულებთ Paper Trade სიმულაციას
    action = data.get('action', 'BUY')
    symbol = data.get('symbol', 'BTCUSDT')
    paper_trader.execute_trade(action, symbol, current_price, qty, sl, tp)
    
    return "სიგნალი მიღებულია", 200

if __name__ == '__main__':
    print("ჩვენი სავაჭრო ბოტი უსმენს სიგნალებს 5000 პორტზე...")
    app.run(port=5000)