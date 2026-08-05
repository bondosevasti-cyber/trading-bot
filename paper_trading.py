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
                # DO NOT save_data() here, otherwise we overwrite the file with empty trades during a read collision
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
        self.load_data()
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

    def get_open_trades(self):
        self.load_data()
        return [t for t in self.trades if t.get("status") == "OPEN"]

    def close_trade(self, trade_id, current_price, reason="CLOSED"):
        self.load_data()
        for t in self.trades:
            if t["id"] == trade_id and t.get("status") == "OPEN":
                action = t["action"]
                entry_price = t["entry_price"]
                qty = t["qty"]
                
                if action == "BUY":
                    pnl = (current_price - entry_price) * qty
                else:
                    pnl = (entry_price - current_price) * qty
                    
                # Add back the original cost plus PnL
                self.balance += t["total_cost"] + pnl
                
                t["status"] = reason
                t["close_price"] = current_price
                t["pnl"] = pnl
                t["close_time"] = datetime.now().isoformat()
                
                print(f"🔄 Trade #{trade_id} {reason} at {current_price}. PnL: ${pnl:.2f}")
                self.save_data()
                return True, pnl
        return False, 0.0

    def close_all(self, current_prices):
        open_trades = self.get_open_trades()
        total_pnl = 0.0
        for t in open_trades:
            symbol = t["symbol"]
            current_price = current_prices.get(symbol)
            if current_price is not None:
                success, pnl = self.close_trade(t["id"], current_price, "CLOSED_PANIC")
                if success:
                    total_pnl += pnl
        return total_pnl

    def get_unrealized_pnl(self, current_prices):
        open_trades = self.get_open_trades()
        pnl = 0.0
        for t in open_trades:
            symbol = t["symbol"]
            current_price = current_prices.get(symbol)
            if current_price is not None:
                if t["action"] == "BUY":
                    pnl += (current_price - t["entry_price"]) * t["qty"]
                else:
                    pnl += (t["entry_price"] - current_price) * t["qty"]
        return pnl
