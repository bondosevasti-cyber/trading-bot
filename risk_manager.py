def calculate_position(entry_price, USD_amount=10, risk_percent=0.01, reward_ratio=2.0):
    # 1. გამოვთვლით რამდენი ცალი კრიპტო მოგვივა $10-ად
    quantity = USD_amount / entry_price
    
    # 2. გამოვთვლით Stop Loss-ს (-1%) და Take Profit-ს (+2%)
    stop_loss = entry_price * (1 - risk_percent)
    take_profit = entry_price * (1 + (risk_percent * reward_ratio))
    
    return round(quantity, 6), round(stop_loss, 2), round(take_profit, 2)

# ვტესტავთ $60,000-იან ბიტკოინზე:
btc_price = 60000
qty, sl, tp = calculate_position(btc_price)

print(f"💵 შესვლის ფასი: ${btc_price}")
print(f"🪙 პოზიციის ზომა ($10-ის): {qty} BTC")
print(f"🛑 Stop Loss (ზარალის ლიმიტი): ${sl}")
print(f"🎯 Take Profit (მოგების სამიზნე): ${tp}")