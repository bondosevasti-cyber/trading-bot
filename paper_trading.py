import json
import os
from datetime import datetime

class PaperTrader:
    def __init__(self, initial_balance=110.0, trades_file="trades.json"):
        self.trades_file = trades_file
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, "r") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", self.initial_balance)
                    self.trades = data.get("trades", [])
            except Exception as e:
                print(f"⚠️ მონაცემების წაკითხვის შეცდომა {self.trades_file}: {e}")
                self.save_data()
        else:
            self.save_data()

    def save_data(self):
        data = {
            "balance": self.balance,
            "trades": self.trades
        }
        with open(self.trades_file, "w") as f:
            json.dump(data, f, indent=4)

    def execute_trade(self, action, symbol, entry_price, qty, stop_loss, take_profit):
        total_cost = round(qty * entry_price, 2)
        
        if self.balance < total_cost:
            print(f"❌ არასაკმარისი ბალანსი! საჭიროა: ${total_cost}, ხელმისაწვდომია: ${self.balance:.2f}")
            return False, "Insufficient balance"

        self.balance -= total_cost
        
        trade = {
            "id": len(self.trades) + 1,
            "action": action,
            "symbol": symbol,
            "entry_price": entry_price,
            "qty": qty,
            "total_cost": total_cost,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": datetime.now().isoformat(),
            "status": "OPEN"
        }

        self.trades.append(trade)
        self.save_data()

        print("=========================================")
        print("📝 PAPER TRADE EXECUTED (ვირტუალური ვაჭრობა)")
        print(f"📊 ტიპი: {action} | სიმბოლო: {symbol}")
        print(f"💵 შესვლის ფასი: ${entry_price:.2f}")
        print(f"🪙 რაოდენობა: {qty}")
        print(f"💰 ჯამური ღირებულება: ${total_cost:.2f}")
        print(f"🛑 Stop Loss: ${stop_loss:.2f}")
        print(f"🎯 Take Profit: ${take_profit:.2f}")
        print(f"💳 განახლებული ვირტუალური ბალანსი: ${self.balance:.2f}")
        print("=========================================")
        return True, trade
