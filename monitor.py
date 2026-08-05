import json
import time
import os
from get_price import get_btc_price

def monitor_trades():
    trades_file = "trades.json"
    print("👀 ვიწყებ ვაჭრობების მონიტორინგს (ყოველ 5 წამში)...")
    
    while True:
        try:
            if not os.path.exists(trades_file):
                time.sleep(5)
                continue
                
            with open(trades_file, "r") as f:
                data = json.load(f)
                
            trades = data.get("trades", [])
            balance = data.get("balance", 0.0)
            
            changes_made = False
            open_trades = [t for t in trades if t.get("status") == "OPEN"]
            
            if open_trades:
                current_price = get_btc_price()
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🔍 ვამოწმებ ფასს: ${current_price:.2f} | ღია პოზიციები: {len(open_trades)}")
                
                for trade in trades:
                    if trade.get("status") != "OPEN":
                        continue
                        
                    sl = trade.get("stop_loss", 0.0)
                    tp = trade.get("take_profit", float('inf'))
                    qty = trade.get("qty", 0.0)
                    
                    closed_status = None
                    
                    if current_price <= sl:
                        closed_status = "CLOSED_SL"
                    elif current_price >= tp:
                        closed_status = "CLOSED_TP"
                        
                    if closed_status:
                        trade["status"] = closed_status
                        revenue = qty * current_price
                        balance += revenue
                        changes_made = True
                        
                        print("=========================================")
                        print(f"🔔 პოზიცია დაიხურა: {closed_status}")
                        print(f"🆔 Trade ID: {trade.get('id')}")
                        print(f"📈 დახურვის ფასი: ${current_price:.2f}")
                        print(f"💰 დაბრუნებული თანხა: ${revenue:.2f}")
                        print(f"💳 განახლებული ბალანსი: ${balance:.2f}")
                        print("=========================================")
                        
            if changes_made:
                data["balance"] = balance
                data["trades"] = trades
                with open(trades_file, "w") as f:
                    json.dump(data, f, indent=4)
                    
        except Exception as e:
            print(f"⚠️ შეცდომა მონიტორინგისას: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    monitor_trades()
