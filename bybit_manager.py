import os
from pybit.unified_trading import HTTP

API_KEY = os.getenv('BYBIT_API_KEY')
API_SECRET = os.getenv('BYBIT_API_SECRET')
TESTNET = os.getenv('BYBIT_TESTNET', 'True') == 'True'

session = None
if API_KEY and API_SECRET:
    try:
        session = HTTP(
            testnet=TESTNET,
            api_key=API_KEY,
            api_secret=API_SECRET,
        )
    except Exception as e:
        print(f"Failed to initialize Bybit session: {e}")

def get_account_balance():
    if not session:
        return 0.0
    try:
        response = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        balance = response['result']['list'][0]['coin'][0]['walletBalance']
        return float(balance)
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0.0

def get_open_positions():
    if not session:
        return []
    try:
        response = session.get_positions(category="linear", settleCoin="USDT")
        positions = response['result']['list']
        open_positions = [p for p in positions if float(p['size']) > 0]
        return open_positions
    except Exception as e:
        print(f"Error getting positions: {e}")
        return []

def get_unrealized_pnl():
    positions = get_open_positions()
    total_pnl = sum([float(p.get('unrealisedPnl', 0)) for p in positions])
    return total_pnl

def close_all_positions():
    if not session:
        return False, "Bybit API Keys not configured."
    try:
        positions = get_open_positions()
        for p in positions:
            symbol = p['symbol']
            side = p['side']
            close_side = "Sell" if side == "Buy" else "Buy"
            session.place_order(
                category="linear",
                symbol=symbol,
                side=close_side,
                orderType="Market",
                qty=p['size'],
                reduceOnly=True
            )
        return True, "All open positions closed successfully."
    except Exception as e:
        print(f"Error closing positions: {e}")
        return False, str(e)
