# Alternative deployment script for Render.com
import os
import threading
import time
import requests
from bot import bot

def keep_alive():
    """Keep the service alive by making periodic requests"""
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        return
    
    while True:
        try:
            response = requests.get(f"{app_url}/health")
            print(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        
        time.sleep(1500)  # 25 minutes

if __name__ == '__main__':
    # Start keep-alive in background
    if os.environ.get('RENDER_EXTERNAL_URL'):
        keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
        keep_alive_thread.start()
    
    # Start the bot
    print("Bot ishga tushdi (Render deployment)...")
    bot.infinity_polling()
