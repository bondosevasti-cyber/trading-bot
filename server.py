import os
import time
import threading
import traceback
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from risk_manager import calculate_position
from get_price import get_price
from paper_trading import PaperTrader

app = Flask(__name__)
paper_trader = PaperTrader(initial_balance=1000.0)

# ----------------- GLOBALS & SETTINGS -----------------
BOT_ACTIVE = True
SETTINGS = {
    'RISK_PERCENT': 2.0,
    'DEFAULT_SL': 1.0,
    'DEFAULT_TP': 2.0,
    'ALLOWED_PAIRS': 'BTCUSDT, ETHUSDT, SOLUSDT, AAPL, TSLA, EURUSD=X, GC=F'
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

# ----------------- BACKGROUND MONITORING --------------
def start_monitoring():
    while True:
        try:
            open_trades = paper_trader.get_open_trades()
            if open_trades:
                symbols = list(set([t["symbol"] for t in open_trades]))
                prices = {}
                for sym in symbols:
                    p = get_price(sym)
                    if p: prices[sym] = p
                
                for t in open_trades:
                    sym = t["symbol"]
                    current_price = prices.get(sym)
                    if current_price:
                        action = t["action"]
                        sl = t["stop_loss"]
                        tp = t["take_profit"]
                        
                        if action == "BUY":
                            if current_price <= sl:
                                paper_trader.close_trade(t["id"], current_price, "CLOSED_SL")
                            elif current_price >= tp:
                                paper_trader.close_trade(t["id"], current_price, "CLOSED_TP")
                        elif action == "SELL":
                            if current_price >= sl:
                                paper_trader.close_trade(t["id"], current_price, "CLOSED_SL")
                            elif current_price <= tp:
                                paper_trader.close_trade(t["id"], current_price, "CLOSED_TP")
        except Exception as e:
            print(f"Monitor Error: {e}")
        time.sleep(5)

monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
monitor_thread.start()

# ----------------- ROUTES -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    try:
        paper_trader.load_data()
        open_trades = paper_trader.get_open_trades()
        symbols = list(set([t["symbol"] for t in open_trades]))
        prices = {}
        for sym in symbols:
            try:
                p = get_price(sym)
                if p: prices[sym] = p
            except Exception as e:
                print(f"Error fetching price for {sym} in status: {e}")

        balance = paper_trader.balance
        pnl = paper_trader.get_unrealized_pnl(prices)

        recent_trades = paper_trader.trades[-5:]
        recent_trades.reverse()

        return jsonify({
            "status": "success",
            "bot_active": BOT_ACTIVE,
            "settings": SETTINGS,
            "latest_signal": latest_signal_data,
            "balance": balance,
            "pnl": pnl,
            "recent_trades": recent_trades
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "bot_active": BOT_ACTIVE,
            "settings": SETTINGS,
            "latest_signal": latest_signal_data,
            "balance": 1000.0,
            "pnl": 0.0,
            "recent_trades": []
        }), 200

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
    open_trades = paper_trader.get_open_trades()
    symbols = list(set([t["symbol"] for t in open_trades]))
    prices = {}
    for sym in symbols:
        p = get_price(sym)
        if p: prices[sym] = p
        
    total_pnl = paper_trader.close_all(prices)
    return jsonify({"success": True, "message": f"All open trades closed. Total realized PnL: ${total_pnl:.2f}"})

@app.route('/api/update-settings', methods=['POST'])
def update_settings():
    global SETTINGS
    data = request.json or {}
    SETTINGS['RISK_PERCENT'] = float(data.get('risk_percent', SETTINGS['RISK_PERCENT']))
    SETTINGS['DEFAULT_SL'] = float(data.get('sl_percent', SETTINGS['DEFAULT_SL']))
    SETTINGS['DEFAULT_TP'] = float(data.get('tp_percent', SETTINGS['DEFAULT_TP']))
    if 'allowed_pairs' in data:
        SETTINGS['ALLOWED_PAIRS'] = data['allowed_pairs']
    return jsonify({"success": True, "settings": SETTINGS})

@app.route('/webhook', methods=['POST'])
def receive_signal():
    global latest_signal_data
    
    if not BOT_ACTIVE:
        print("⚠️ სიგნალი იგნორირებულია: ბოტი გათიშულია.")
        return "ბოტი გათიშულია", 200

    data = request.json or {}
    print("=========================================")
    print(f"🚨 მივიღეთ ახალი სიგნალი: {data}")
    
    symbol = data.get('symbol', 'BTCUSDT').upper()
    allowed_pairs = [s.strip().upper() for s in SETTINGS['ALLOWED_PAIRS'].split(',')]
    if symbol not in allowed_pairs:
        print(f"⚠️ სიგნალი იგნორირებულია: სიმბოლო {symbol} არ არის დაშვებულ სიაში.")
        return f"Symbol {symbol} not allowed", 200
    
    current_price = data.get('price')
    if current_price:
        try:
            current_price = float(current_price)
            print(f"💲 ფასი წამოვიდა პირდაპირ სიგნალიდან: ${current_price}")
        except ValueError:
            current_price = None
            
    if current_price is None:
        current_price = get_price(symbol)
        
    if current_price is None:
        print(f"❌ ფასის მიღება ვერ მოხერხდა {symbol}-სთვის.")
        traceback.print_exc()
        return "ფასის მიღება ვერ მოხერხდა", 500
    
    action = data.get('action', 'BUY').upper()
    
    sl_fraction = SETTINGS['DEFAULT_SL'] / 100.0
    reward_ratio = SETTINGS['DEFAULT_TP'] / SETTINGS['DEFAULT_SL'] if SETTINGS['DEFAULT_SL'] > 0 else 2.0
    usd_amount = (SETTINGS['RISK_PERCENT'] / 100.0) * paper_trader.balance
    
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
    
    print(f"📈 {symbol} მიმდინარე ფასი: ${current_price}")
    print(f"🪙 პოზიციის ზომა: {qty}")
    print(f"🛑 Stop Loss: ${sl}")
    print(f"🎯 Take Profit: ${tp}")
    print("=========================================")
    
    success, trade = paper_trader.execute_trade(action, symbol, current_price, qty, sl, tp)
    if not success:
        return "Insufficient virtual balance", 400
        
    return "სიგნალი მიღებულია და გაიხსნა ვირტუალური პოზიცია", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"ჩვენი სავაჭრო ბოტი უსმენს სიგნალებს {port} პორტზე...")
    app.run(host='0.0.0.0', port=port)