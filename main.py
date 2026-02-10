import os
import requests
import telebot
from flask import Flask

# 1. Setup
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 2. Cricbuzz Data Fetcher Logic
def get_live_scores():
    url = "https://www.cricbuzz.com/api/home"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.cricbuzz.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            messages = []
            
            # Sirf pehle 5 matches dikhayenge taaki message bahut bada na ho
            for item in data.get('matches', [])[:5]:
                m = item.get('match', {})
                info = m.get('matchInfo', {})
                score = m.get('matchScore', {})
                
                t1 = info.get('team1', {}).get('teamSName', 'T1')
                t2 = info.get('team2', {}).get('teamSName', 'T2')
                status = info.get('status', 'No Status')
                
                if score:
                    # Score nikalne ka logic
                    s1 = score.get('team1Score', {}).get('inngs1', {})
                    s2 = score.get('team2Score', {}).get('inngs1', {})
                    
                    msg = (f"🏏 *{t1} vs {t2}*\n"
                           f"🔹 {t1}: {s1.get('runs', 0)}/{s1.get('wickets', 0)} ({s1.get('overs', 0)})\n"
                           f"🔹 {t2}: {s2.get('runs', 0)}/{s2.get('wickets', 0)} ({s2.get('overs', 0)})\n"
                           f"📢 _{status}_\n")
                else:
                    msg = f"🕒 *{t1} vs {t2}*\n📢 _{status}_\n"
                
                messages.append(msg)
            
            return "\n---\n".join(messages) if messages else "No live matches found."
        return "❌ Server se data nahi mila."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 3. Bot Command
@bot.message_handler(commands=['score'])
def send_score(message):
    score_update = get_live_scores()
    bot.reply_to(message, score_update, parse_mode="Markdown")

# 4. Flask Route (For Render/Deployment)
@app.route('/')
def index():
    return "Bot is Running!"

if __name__ == "__main__":
    # Bot ko background mein start karein
    print("Bot starting...")
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    # Flask app ko port par run karein
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
