import os
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from risk_manager import calculate_position
from get_price import get_btc_price  # 1. შემოვპორტოთ ფასის წამოღების ფუნქცია
from paper_trading import PaperTrader

app = Flask(__name__)
paper_trader = PaperTrader(initial_balance=110.0)

latest_signal_data = {
    "action": "-",
    "symbol": "-",
    "current_price": 0.0,
    "qty": 0.0,
    "sl": 0.0,
    "tp": 0.0,
    "timestamp": "ჯერ არ არის სიგნალი"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify(latest_signal_data)

@app.route('/webhook', methods=['POST'])
def receive_signal():
    data = request.json or {}
    print("=========================================")
    print(f"🚨 მივიღეთ ახალი სიგნალი: {data}")
    
    # 2. ვიღებთ ბიტკოინის რეალურ ფასს ბირჟიდან
    current_price = get_btc_price()
    if current_price is None:
        print("❌ ფასის მიღება ვერ მოხერხდა")
        return "ფასის მიღება ვერ მოხერხდა", 500
    
    action = data.get('action', 'BUY')
    symbol = data.get('symbol', 'BTCUSDT')
    
    # 3. ვითვლით რისკებს რეალური ფასის მიხედვით
    qty, sl, tp = calculate_position(current_price, action=action)
    
    global latest_signal_data
    latest_signal_data.update({
        "action": action,
        "symbol": symbol,
        "current_price": current_price,
        "qty": qty,
        "sl": sl,
        "tp": tp,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    print(f"📈 მიმდინარე ფასი: ${current_price}")
    print(f"🪙 პოზიციის ზომა ($10-ის): {qty} BTC")
    print(f"🛑 Stop Loss: ${sl}")
    print(f"🎯 Take Profit: ${tp}")
    print("=========================================")
    
    # 4. ვასრულებთ Paper Trade სიმულაციას
    paper_trader.execute_trade(action, symbol, current_price, qty, sl, tp)
    
    return "სიგნალი მიღებულია", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"ჩვენი სავაჭრო ბოტი უსმენს სიგნალებს {port} პორტზე...")
    app.run(host='0.0.0.0', port=port)