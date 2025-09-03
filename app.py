from flask import Flask, jsonify
import threading
import time
import requests
import os
from bot import bot

app = Flask(__name__)

# Keep-alive endpoint
@app.route('/')
def home():
    return jsonify({
        "status": "Bot is running",
        "message": "Telegram bot is active and working!"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Keep-alive function to prevent sleeping
def keep_alive():
    """Send periodic requests to keep the service awake"""
    while True:
        try:
            # Get the app URL from environment or use a default
            app_url = os.environ.get('APP_URL', 'http://localhost:5000')
            if app_url != 'http://localhost:5000':
                response = requests.get(f"{app_url}/health")
                print(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        
        # Wait 25 minutes before next ping (to prevent 30min timeout)
        time.sleep(1500)  # 25 minutes

# Start bot in a separate thread
def start_bot():
    print("Starting Telegram bot...")
    bot.infinity_polling()

if __name__ == '__main__':
    # Start keep-alive in background
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Start bot in background
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
