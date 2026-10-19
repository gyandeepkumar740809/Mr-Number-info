import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. अपना Telegram Bot Token यहाँ डालें
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# 2. अपनी Phone Lookup API का URL और Key यहाँ सेट करें
API_URL = "https://api.yourprovider.com/lookup?phone="
API_KEY = "YOUR_API_KEY"  # अगर API key की ज़रूरत न हो, तो इसे ख़ाली छोड़ दें ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **OSINT Phone Lookup Bot में आपका स्वागत है!**\n\n"
        "कंट्री कोड के साथ कोई भी फ़ोन नंबर भेजें (जैसे: +919876543210)।",
        parse_mode="Markdown"
    )

async def search_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()
    
    # फ़ोन नंबर वैलिडेशन Check
    if not phone_number.replace("+", "").isdigit() or len(phone_number) < 10:
        await update.message.reply_text("❌ कृपया एक मान्य फ़ोन नंबर भेजें (जैसे: +919876543210)।")
        return

    await update.message.reply_text(f"🔍 `{phone_number}` की जानकारी खोजी जा रही है...", parse_mode="Markdown")

    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        response = requests.get(f"{API_URL}{phone_number}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # API के रिस्पॉन्स के अनुसार डेटा फ़ॉर्मेट करें
            result_text = (
                f"📊 **OSINT Results for:** `{phone_number}`\n\n"
                f"👤 **Name / Owner:** {data.get('name', 'N/A')}\n"
                f"📍 **Location:** {data.get('location', 'N/A')}\n"
                f"📡 **Carrier:** {data.get('carrier', 'N/A')}\n"
                f"🌐 **Country:** {data.get('country', 'N/A')}\n"
            )
            await update.message.reply_text(result_text, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ API से जानकारी प्राप्त नहीं हो सकी या नंबर नहीं मिला।")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ कनेक्शन त्रुटि। कृपया बाद में प्रयास करें।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_phone))

    print("Bot is running...")
    app.run_polling()
  
