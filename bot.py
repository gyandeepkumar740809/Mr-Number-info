import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "8673175767:AAEj5mYaj3S-9ctsGtRpD8cXU8YAB3_S5Pc"
API_URL = "http://api-stark-d4bb.vercel.app/alam-adr?adr=value"
API_KEY = "YOUR_API_KEY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 OSINT Phone Lookup Bot में स्वागत है!\n\n"
        "कंट्री कोड के साथ फ़ोन नंबर भेजें (जैसे: +919876543210)।"
    )

async def search_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text.strip()
    
    if not phone_number.replace("+", "").isdigit() or len(phone_number) < 10:
        await update.message.reply_text("❌ कृपया एक मान्य फ़ोन नंबर भेजें।")
        return

    await update.message.reply_text(f"🔍 `{phone_number}` की जानकारी खोजी जा रही है...", parse_mode="Markdown")

    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        response = requests.get(f"{API_URL}{phone_number}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result_text = (
                f"📊 **OSINT Results for:** `{phone_number}`\n\n"
                f"👤 **Name:** {data.get('name', 'N/A')}\n"
                f"📍 **Location:** {data.get('location', 'N/A')}\n"
                f"📡 **Carrier:** {data.get('carrier', 'N/A')}\n"
                f"🌐 **Country:** {data.get('country', 'N/A')}\n"
            )
            await update.message.reply_text(result_text, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ API से जानकारी प्राप्त नहीं हो सकी।")
            
    except Exception as e:
        await update.message.reply_text("❌ कनेक्शन त्रुटि। कृपया बाद में प्रयास करें।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_phone))

    print("Bot is running...")
    app.run_polling()
  
