import telebot
import requests

# 1. Setup: Apna Token yahan daalein
BOT_TOKEN = "8215508330:AAH89E2yXIslUZDwb3gIkxgeHdEzLnR7EVk"
bot = telebot.TeleBot(BOT_TOKEN)

# 2. Score Fetching Function
def fetch_cricbuzz_scores():
    url = "https://www.cricbuzz.com/api/home"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.cricbuzz.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "❌ API access nahi ho pa rahi hai."

        data = response.json()
        match_list = data.get('matches', [])
        
        if not match_list:
            return "📭 Abhi koi live matches nahi mil rahe hain."

        final_msg = "🏏 *LIVE CRICKET SCORES* 🏏\n\n"

        # Hum pehle 5 matches ka data nikalenge
        for item in match_list[:5]:
            match = item.get('match', {})
            info = match.get('matchInfo', {})
            score = match.get('matchScore', {})

            t1 = info.get('team1', {}).get('teamSName', 'T1')
            t2 = info.get('team2', {}).get('teamSName', 'T2')
            status = info.get('status', 'Status unavailable')

            # Match Score Formatting
            if score:
                # Team 1 Score
                s1 = score.get('team1Score', {}).get('inngs1', {})
                runs1 = s1.get('runs', 0)
                wkts1 = s1.get('wickets', 0)
                ovrs1 = s1.get('overs', 0)

                # Team 2 Score
                s2 = score.get('team2Score', {}).get('inngs1', {})
                runs2 = s2.get('runs', 0)
                wkts2 = s2.get('wickets', 0)
                ovrs2 = s2.get('overs', 0)

                match_text = (f"⭐ *{t1} vs {t2}*\n"
                              f"🔹 {t1}: {runs1}/{wkts1} ({ovrs1})\n"
                              f"🔹 {t2}: {runs2}/{wkts2} ({ovrs2})\n"
                              f"📢 _{status}_\n\n")
            else:
                # Agar match abhi shuru nahi hua (Preview/Toss)
                match_text = (f"⭐ *{t1} vs {t2}*\n"
                              f"📢 _{status}_\n\n")
            
            final_msg += match_text

        return final_msg

    except Exception as e:
        return f"⚠️ Error aa gaya: {str(e)}"

# 3. Bot Command Handlers
@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "Welcome! Live cricket score dekhne ke liye `/score` likhein.", parse_mode="Markdown")

@bot.message_handler(commands=['score'])
def send_score(message):
    bot.send_chat_action(message.chat.id, 'typing')
    result = fetch_cricbuzz_scores()
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

# 4. Start Bot
print("Bot is running...")
bot.infinity_polling()
