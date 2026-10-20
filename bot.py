import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Aapka Telegram Bot Token
TOKEN = "8673175767:AAEj5mYaj3S-9ctsGtRpD8cXU8YAB3_S5Pc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 OSINT Phone Lookup Bot mein swagat hai!\n\nKripya 10 anko ka phone number ya country code ke sath number bhejein (jaise: 9876543210)."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Yadi user ne sirf 10 anko ka number bheja hai, to +91 jod dein
    if text.isdigit() and len(text) == 10:
        phone_number = "+91" + text
    elif text.startswith("+") and text[1:].isdigit():
        phone_number = text
    else:
        await update.message.reply_text("❌ Kripya vaidya 10 anko ka phone number darj karein.")
        return

    await update.message.reply_text(f"🔍 {phone_number} ki jankari khoji ja rahi hai...")

    try:
        # API URL me phone number/query pass karna
        api_url = f"http://api-stark-d4bb.vercel.app/alam-adr?adr={phone_number}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # API response ke anusaar fields set karein (yahan example ke taur par data dikhaya gaya hai)
            name = data.get('name', 'N/A')
            location = data.get('location', 'N/A')
            carrier = data.get('carrier', 'N/A')
            country = data.get('country', 'N/A')
            
            response_text = (
                f"📊 **OSINT Results for: {phone_number}**\n\n"
                f"👤 **Name:** {name}\n"
                f"📍 **Location:** {location}\n"
                f"📡 **Carrier:** {carrier}\n"
                f"🌍 **Country:** {country}"
            )
        else:
            response_text = "❌ API se data fetch karne mein samasya aayi. Kripya baad mein prayas karein."
            
    except Exception as e:
        logger.error(f"Error fetching API: {e}")
        response_text = "❌ Error: API request fail ho gayi."
    
    await update.message.reply_text(response_text, parse_mode="Markdown")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot started successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
  
