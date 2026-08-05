import os
import traceback
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from risk_manager import calculate_position
from get_price import get_btc_price
from paper_trading import PaperTrader
import bybit_manager

app = Flask(__name__)
paper_trader = PaperTrader(initial_balance=110.0)

# ----------------- GLOBALS & SETTINGS -----------------
BOT_ACTIVE = True
SETTINGS = {
    'RISK_PERCENT': 2.0,   # Capital risk per trade
    'DEFAULT_SL': 1.0,     # Stop Loss %
    'DEFAULT_TP': 2.0      # Take Profit %
}

latest_signal_data = {
    "action": "-",
    "symbol": "-",
    "current_price": 0.0,
    "qty": 0.0,
    "sl": 0.0,
    "tp": 0.0,
    "timestamp": "ჯერ არ არის სიგნალი"
}

# ----------------- ROUTES -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    # Fetch real Bybit balance and PnL
    balance = bybit_manager.get_account_balance()
    pnl = bybit_manager.get_unrealized_pnl()
    
    # Fallback to paper trading balance if Bybit API is not set up
    if balance == 0.0 and pnl == 0.0:
        paper_trader.load_data()
        balance = paper_trader.balance

    # Get recent trades
    paper_trader.load_data()
    recent_trades = paper_trader.trades[-5:]
    recent_trades.reverse() # Show newest first

    return jsonify({
        "bot_active": BOT_ACTIVE,
        "settings": SETTINGS,
        "latest_signal": latest_signal_data,
        "balance": balance,
        "pnl": pnl,
        "recent_trades": recent_trades
    })

@app.route('/api/toggle-bot', methods=['POST'])
def toggle_bot():
    global BOT_ACTIVE
    data = request.json or {}
    if 'active' in data:
        BOT_ACTIVE = data['active']
    else:
        BOT_ACTIVE = not BOT_ACTIVE
    return jsonify({"success": True, "bot_active": BOT_ACTIVE})

@app.route('/api/close-all', methods=['POST'])
def close_all():
    success, msg = bybit_manager.close_all_positions()
    # Also simulate closing in paper trader
    return jsonify({"success": success, "message": msg})

@app.route('/api/update-settings', methods=['POST'])
def update_settings():
    global SETTINGS
    data = request.json or {}
    SETTINGS['RISK_PERCENT'] = float(data.get('risk_percent', SETTINGS['RISK_PERCENT']))
    SETTINGS['DEFAULT_SL'] = float(data.get('sl_percent', SETTINGS['DEFAULT_SL']))
    SETTINGS['DEFAULT_TP'] = float(data.get('tp_percent', SETTINGS['DEFAULT_TP']))
    return jsonify({"success": True, "settings": SETTINGS})

@app.route('/webhook', methods=['POST'])
def receive_signal():
    global latest_signal_data
    
    if not BOT_ACTIVE:
        print("⚠️ სიგნალი იგნორირებულია: ბოტი გათიშულია (Paused).")
        return "ბოტი გათიშულია", 200

    data = request.json or {}
    print("=========================================")
    print(f"🚨 მივიღეთ ახალი სიგნალი: {data}")
    
    # 2. ვიღებთ ბიტკოინის ფასს (ჯერ ვამოწმებთ Payload-ს, შემდეგ API-ს)
    current_price = data.get('price')
    if current_price:
        try:
            current_price = float(current_price)
            print(f"💲 ფასი წამოვიდა პირდაპირ სიგნალიდან: ${current_price}")
        except ValueError:
            current_price = None
            
    if current_price is None:
        current_price = get_btc_price()
        
    if current_price is None:
        print("❌ ფასის მიღება ვერ მოხერხდა არც სიგნალიდან და არც API-დან.")
        traceback.print_exc()
        return "ფასის მიღება ვერ მოხერხდა", 500
    
    action = data.get('action', 'BUY')
    symbol = data.get('symbol', 'BTCUSDT')
    
    # Translate SETTINGS to calculate_position parameters
    # calculate_position takes risk_percent (fraction) and reward_ratio
    sl_fraction = SETTINGS['DEFAULT_SL'] / 100.0
    reward_ratio = SETTINGS['DEFAULT_TP'] / SETTINGS['DEFAULT_SL'] if SETTINGS['DEFAULT_SL'] > 0 else 2.0
    usd_amount = SETTINGS['RISK_PERCENT'] * 10 # simplistic representation for 1000$ portfolio
    
    # 3. ვითვლით რისკებს რეალური ფასის მიხედვით
    qty, sl, tp = calculate_position(current_price, action=action, USD_amount=usd_amount, risk_percent=sl_fraction, reward_ratio=reward_ratio)
    
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
    print(f"🪙 პოზიციის ზომა: {qty} BTC")
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