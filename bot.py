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
        "👋 OSINT Phone Lookup Bot mein swagat hai!\n\nKripya sirf 10 anko ka phone number bhejein (jaise: 9876543210)."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # JSON file ke anusaar API sirf 10 digits ka number maangti hai[span_1](start_span)[span_1](end_span)
    if text.startswith("+91") and len(text) == 13:
        phone_number = text[3:]
    elif text.startswith("91") and len(text) == 12:
        phone_number = text[2:]
    elif text.isdigit() and len(text) == 10:
        phone_number = text
    else:
        await update.message.reply_text("❌ Kripya keval 10 anko ka valid phone number darj karein.")
        return

    await update.message.reply_text(f"🔍 {phone_number} ki jankari khoji ja rahi hai...")

    try:
        api_url = f"http://api-stark-d4bb.vercel.app/alam-adr?adr={phone_number}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Agar API se error message aaye[span_2](start_span)[span_2](end_span)
            if data.get('status') == 'error':
                error_msg = data.get('message', 'Invalid mobile number')
                response_text = f"❌ API Error: {error_msg}"
            else:
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
            response_text = "❌ API se data fetch karne mein samasya aayi."
            
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
  
