import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION & API KEYS ---
# Aapka Naya Bot Token direct setup kar diya gaya hai
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8673175767:AAEj5mYaj3S-9ctsGtRpD8cXU8YAB3_S5Pc")

# APIs Configuration (Yahan apni working APIs ke URLs dalein)
INSTA_API_URL = "https://your-instagram-api.com/api" 
NUM_API_URL = "https://your-number-api.com/api"     
DARK_DATA_API_URL = "https://your-darkdata-api.com/api" 

# --- COMMAND HANDLERS ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler - Bina kisi channel join condition ke simple welcome message
    """
    welcome_text = (
        "👋 **Welcome to Phoenix Osint Bot!**\n\n"
        "Aap is bot se seedhe jankari nikal sakte hain:\n"
        "1. **Instagram Info:** User's `@username` bhejin.\n"
        "2. **Phone Details:** `10-digit mobile number` bhejin.\n"
        "3. **Dark Data / Leak Search:** Koi bhi email/username/data query bhejin.\n\n"
        "Kisi bhi channel ko join karne ki zaroorat nahi hai. Seedha search karein!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help command handler
    """
    help_text = (
        "📌 **Kaise istemal karein?**\n\n"
        "• Mobile Number ki detail ke liye: `9876543210`\n"
        "• Instagram Profile ke liye: `@username`\n"
        "• Leak/Breach Data ke liye: Kisi bhi search term ko type karein."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# --- MESSAGE PROCESSING ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # 1. Phone Number Lookup (10 Digits)
    if re.match(r'^\d{10}$', text):
        await update.message.reply_text("🔎 Mobile number detail fetch ho rahi hai, kripya intezar karein...")
        try:
            response = requests.get(f"{NUM_API_URL}?num={text}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                msg = f"📱 **Number Details:**\n\n{data.get('result', 'Details nahi mil saki.')}"
            else:
                msg = "❌ API Request fail ho gayi. Kripya baad mein try karein."
        except Exception as e:
            msg = "⚠️ Server connection issue ya API timeout."
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 2. Instagram Profile Lookup (@username)
    if text.startswith("@"):
        username = text.replace("@", "").strip()
        await update.message.reply_text(f"📸 `@{username}` ki Instagram profile fetch ho rahi hai...", parse_mode="Markdown")
        try:
            response = requests.get(f"{INSTA_API_URL}?username={username}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                msg = f"👤 **Instagram Profile Info:**\n\n{data.get('result', 'Profile details nahi mili.')}"
            else:
                msg = "❌ Instagram API fail ho gayi."
        except Exception as e:
            msg = "⚠️ Connection error."
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 3. Dark Data / General Leak Lookup
    await update.message.reply_text("🔍 Dark Data / Breach database search kiya ja raha hai...")
    try:
        response = requests.get(f"{DARK_DATA_API_URL}?query={text}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            msg = f"📊 **Search Results:**\n\n{data.get('result', 'Koi data nahi mila.')}"
        else:
            msg = "❌ Data fetch nahi ho saka."
    except Exception as e:
        msg = "⚠️ API request error."

    await update.message.reply_text(msg, parse_mode="Markdown")

# --- MAIN BOT RUNNER ---

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers Add Karein
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot chalu ho gaya hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
