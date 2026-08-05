import requests
import json

def send_test_signal(action="BUY", symbol="BTC"):
    url = "http://localhost:5000/webhook"
    payload = {
        "action": action,
        "asset": symbol
    }
    
    print(f"🚀 Sending POST request to {url} ...")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\n✅ Status Code: {response.status_code}")
        try:
            # Try to print as JSON if the server returns JSON
            print(f"📩 Response (JSON): {response.json()}")
        except json.JSONDecodeError:
            # Fallback to printing plain text (Flask server currently returns plain text)
            print(f"📩 Response (Text): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error connecting to server: {e}")
        print("💡 Make sure your Flask server (server.py) is running on port 5000.")

if __name__ == "__main__":
    # Send a test BUY signal immediately when running the script
    send_test_signal()
