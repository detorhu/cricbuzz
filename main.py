import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Apna token yahan daalein
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- SCORE FETCHER LOGIC ---
def get_live_scores():
    # 1. Cache-Busting: URL ke end mein current timestamp add kiya taaki server fresh data de
    timestamp = int(time.time() * 1000)
    url = f"https://www.cricbuzz.com/api/home?v={timestamp}"
    
    # 2. Strict No-Cache Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.cricbuzz.com/",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    try:
        # 3. Requesting Data
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if not matches:
                return "📭 Abhi koi live match nahi mil raha hai."

            final_msg = "🏏 *REAL-TIME LIVE SCORES* 🏏\n\n"
            
            # Top 5 matches process karein
            for item in matches[:5]:
                m = item.get('match', {})
                info = m.get('matchInfo', {})
                score = m.get('matchScore', {})
                
                t1 = info.get('team1', {}).get('teamSName', 'T1')
                t2 = info.get('team2', {}).get('teamSName', 'T2')
                status = info.get('status', 'No Status')
                
                if score:
                    # Score details extract karein
                    s1 = score.get('team1Score', {}).get('inngs1', {})
                    s2 = score.get('team2Score', {}).get('inngs1', {})
                    
                    # Formatting
                    msg = (f"⭐ *{t1} vs {t2}*\n"
                           f"🔹 {t1}: {s1.get('runs', 0)}/{s1.get('wickets', 0)} ({s1.get('overs', 0)})\n"
                           f"🔹 {t2}: {s2.get('runs', 0)}/{s2.get('wickets', 0)} ({s2.get('overs', 0)})\n"
                           f"📢 _{status}_\n\n")
                else:
                    # Match Preview
                    msg = f"🕒 *{t1} vs {t2}*\n📢 _{status}_\n\n"
                
                final_msg += msg
            
            return final_msg
        else:
            return "❌ API Error: Data fetch nahi ho paya."
            
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Pro Cricket Bot Active! 🚀\nLive score dekhne ke liye `/score` bhejein.", parse_mode="Markdown")

@bot.message_handler(commands=['score'])
def send_score(message):
    bot.send_chat_action(message.chat.id, 'typing')
    update = get_live_scores()
    bot.reply_to(message, update, parse_mode="Markdown")

# --- DEPLOYMENT HELPERS (Flask) ---
@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    print("Bot polling started...")
    bot.infinity_polling()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Flask aur Bot dono ko alag threads mein chalana taaki Render use sleep na kare
    Thread(target=run_flask).start()
    run_bot()
                
