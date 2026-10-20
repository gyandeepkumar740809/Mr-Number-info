import os
import logging
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "8673175767:AAEj5mYaj3S-9ctsGtRpD8cXU8YAB3_S5Pc"

# ========== 🔧 API CONFIGURATIONS ==========
API_BASE = "https://anon-insta-info.vercel.app/basic"
API_KEY  = "Anish@ExpAnonx1410"

DARK_API = "https://dark-api-hub.onrender.com/api/Insta"
DARK_KEY = "Anish300paid"

NUM_API  = "https://anon-num-info.vercel.app/num"
NUM_KEY  = "Anish@Key_1608"
# ============================================

def format_aadhaar(aadhaar):
    clean = re.sub(r'\D', '', str(aadhaar))
    if len(clean) == 12:
        return f"{clean[:4]} {clean[4:8]} {clean[8:]}"
    return str(aadhaar)

def clean_address(addr):
    if not addr or addr == 'N/A':
        return 'N/A'
    addr = str(addr).replace('!', ', ')
    addr = re.sub(r',\s*,+', ', ', addr)
    addr = re.sub(r'\s+', ' ', addr)
    return addr.strip(', ')

def extract_field(arr, keys, default='N/A'):
    for k in keys:
        if k in arr and arr[k]:
            return arr[k]
    return default

def pick_best_record(records, target_num=''):
    if not records:
        return None
    
    if target_num:
        exact = [r for r in records if r.get('num') == target_num]
        if exact:
            records = exact

    best = None
    best_score = -1
    for rec in records:
        score = 0
        if rec.get('aadhar'): score += 1000
        if rec.get('name') and rec.get('name') != 'N/A': score += 100
        if rec.get('fname'): score += 50
        if rec.get('address') and len(str(rec.get('address'))) > 20: score += 50
        if rec.get('email') and '@' in str(rec.get('email')): score += 30
        if rec.get('circle'): score += 10
        if rec.get('alt'): score += 5
        
        if score > best_score:
            best_score = score
            best = rec
    return best

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **OSINT & Instagram Lookup Bot mein swagat hai!**\n\n"
        "Kripya koi bhi **Instagram username** (jaise: `tondog`) ya **10 anko ka mobile number** bhejein.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Check karein ki user ne phone number bheja hai ya username
    clean_text = re.sub(r'\D', '', text)
    if len(clean_text) >= 10:
        # Agar number bheja hai toh seedhe Number Lookup API chalayein
        phone_clean = clean_text[-10:]
        await handle_number_lookup(update, phone_clean)
    else:
        # Agar text/username hai toh Instagram aur Breach API chalayein
        clean_username = text.lstrip('@').strip()
        if not clean_username:
            await update.message.reply_text("❌ Kripya ek valid Instagram username ya mobile number bhejein.")
            return
        await handle_insta_lookup(update, clean_username)

async def handle_number_lookup(update, phone_clean):
    await update.message.reply_text(f"🔍 `{phone_clean}` ki mobile jankari khoji ja rahi hai, kripya pratiksha karein...", parse_mode="Markdown")
    
    output = "📱 **NUMBER INFORMATION LOOKUP**\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    output += f"├ 📞 Number      : {phone_clean}\n"

    url3 = f"{NUM_API}?key={NUM_KEY}&num={phone_clean}"
    try:
        res3 = requests.get(url3, timeout=20)
        if res3.status_code == 200:
            json3 = res3.json()
            num_records = json3.get('response', {}).get('data', [])
            
            if num_records and isinstance(num_records, list):
                num_data = pick_best_record(num_records, phone_clean)
                if num_data:
                    n_name = extract_field(num_data, ['name', 'full_name', 'fullname'])
                    n_fname = extract_field(num_data, ['fname', 'father_name', 'father', 'fathername'])
                    n_aadhaar = extract_field(num_data, ['aadhar', 'aadhaar', 'adhar', 'adhaar', 'uid', 'uidai'])
                    n_address = clean_address(extract_field(num_data, ['address', 'addr', 'location']))
                    n_circle = extract_field(num_data, ['circle', 'operator', 'state'])
                    n_email = extract_field(num_data, ['email', 'mail'])
                    n_alt = extract_field(num_data, ['alt', 'alt_number', 'alternate'])

                    output += f"├ 📛 Name        : {n_name}\n"
                    output += f"├ 👨 Father Name : {n_fname}\n"

                    if n_aadhaar != 'N/A' and n_aadhaar:
                        output += f"├ 🪪 Aadhaar     : <code>{format_aadhaar(n_aadhaar)}</code>\n"
                    else:
                        output += "├ 🪪 Aadhaar     : ❌ Not Available\n"

                    output += f"├ 📍 Address     : {n_address}\n"
                    output += f"├ 📡 Circle      : {n_circle}\n"
                    output += f"├ 📧 Email       : {n_email}\n"
                    output += f"└ 📱 Alt Number  : {n_alt}\n\n"
                    output += f"📊 <b>Total {len(num_records)} records found</b>\n"
                else:
                    output += "└ ❌ Number detail not found in records\n"
            else:
                output += "└ ❌ Number detail not found\n"
    except Exception as e:
        logger.error(f"Number API Error: {e}")
        output += "└ ❌ Number info fetch error\n"

    output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "💳 BUY API : @Vectraen\n"
    output += "🆘 SUPPORT : @Vectraen\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    await update.message.reply_text(output, parse_mode="HTML")

async def handle_insta_lookup(update, clean_username):
    await update.message.reply_text(f"🔍 `@{clean_username}` ki jankari khoji ja rahi hai, kripya pratiksha karein...", parse_mode="Markdown")

    # API 1: Instagram Profile
    url1 = f"{API_BASE}?key={API_KEY}&username={clean_username}"
    profile_ok = False
    account, metrics, bio = {}, {}, {}

    try:
        res1 = requests.get(url1, timeout=20)
        if res1.status_code == 200:
            json1 = res1.json()
            if json1.get('response', {}).get('parameters', {}).get('success') is True:
                data1_list = json1.get('response', {}).get('data', [])
                if data1_list and isinstance(data1_list, list):
                    insta_profile = data1_list[0].get('instagram_profile', {})
                    if insta_profile:
                        profile_ok = True
                        account = insta_profile.get('account_info', {})
                        metrics = insta_profile.get('metrics', {})
                        bio = insta_profile.get('biography_data', {})
    except Exception as e:
        logger.error(f"API 1 Error: {e}")

    # API 2: Dark / Contact Data
    url2 = f"{DARK_API}?key={DARK_KEY}&Insta={clean_username}"
    dark_ok = False
    contact, sources = {}, {}

    try:
        res2 = requests.get(url2, timeout=25)
        if res2.status_code == 200:
            json2 = res2.json()
            if json2.get('success') and json2.get('results'):
                dark_ok = True
                contact = json2.get('results', [{}])[0]
                sources = json2.get('sources', {})
    except Exception as e:
        logger.error(f"API 2 Error: {e}")

    if not profile_ok and not dark_ok:
        await update.message.reply_text(f"❌ '{clean_username}' ke liye koi data nahi mila.\n\n💳 BUY API : @Vectraen")
        return

    output = "📸 **INSTAGRAM FULL LOOKUP**\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if profile_ok:
        user_id = account.get('user_id', 'N/A')
        username_disp = account.get('username', clean_username)
        full_name = account.get('full_name', 'N/A')
        profile_url = account.get('profile_url', f"https://instagram.com/{username_disp}")
        is_private = bool(account.get('is_private'))
        is_verified = bool(account.get('is_verified'))
        is_business = bool(account.get('is_business_account'))

        posts = metrics.get('total_posts_count', 0)
        followers = metrics.get('followers_count', 0)
        following = metrics.get('following_count', 0)

        biography = bio.get('text', 'N/A')
        external_urls = bio.get('external_urls', [])

        output += "👤 **PROFILE INFORMATION**\n"
        output += f"├ 🆔 User ID     : `{user_id}`\n"
        output += f"├ 📛 Username    : @{username_disp}\n"
        output += f"├ 👤 Full Name   : {full_name}\n"
        output += f"├ 🔗 Profile URL : {profile_url}\n"
        output += f"├ 🔒 Privacy     : {'🔒 Private' if is_private else '🌐 Public'}\n"
        output += f"├ ✅ Verified    : {'✅ Yes' if is_verified else '❌ No'}\n"
        output += f"└ 🏢 Business    : {'✅ Yes' if is_business else '❌ No'}\n\n"

        output += "📊 **METRICS**\n"
        output += f"├ 📸 Posts       : {posts:,}\n"
        output += f"├ 👥 Followers   : {followers:,}\n"
        output += f"└ 👣 Following   : {following:,}\n\n"

        output += "📝 **BIOGRAPHY**\n"
        for line in biography.split('\n'):
            output += f"│ {line}\n"

        if external_urls and isinstance(external_urls, list):
            output += "\n🔗 **EXTERNAL LINKS**\n"
            for url in external_urls:
                output += f"└ {url}\n"
    else:
        output += "👤 **PROFILE INFORMATION**\n└ ❌ No profile data found\n\n"

    if dark_ok:
        output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "📇 **CONTACT / BREACH INFO**\n"
        output += f"├ 📛 Name        : {contact.get('name', 'N/A')}\n"
        output += f"├ 📧 Email       : {contact.get('email', 'N/A')}\n"
        output += f"├ 📱 Phone       : {contact.get('phone', 'N/A')}\n"
        output += f"├ 📍 Address     : {contact.get('address', 'N/A')}\n"
        output += f"├ 🆔 User ID     : {contact.get('id', 'N/A')}\n"
        output += f"└ 🔗 Username    : {contact.get('username', 'N/A')}\n"

        if sources:
            db1 = 1 if sources.get('db1_17M') else 0
            db2 = 1 if sources.get('db2_4.9M') else 0
            output += "\n📊 **DB SOURCE**\n"
            output += f"├ DB1 (17M)     : {'✅ Found' if db1 else '❌ Not Found'}\n"
            output += f"└ DB2 (4.9M)   : {'✅ Found' if db2 else '❌ Not Found'}\n"
    else:
        output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "📇 **CONTACT / BREACH INFO**\n└ ❌ No contact data found\n"

    # Agar contact mein phone number milta hai toh API 3 se uska bhi number lookup run kar dein
    phone_to_lookup = contact.get('phone', '')
    phone_clean = re.sub(r'\D', '', str(phone_to_lookup))
    if phone_clean.startswith('91') and len(phone_clean) == 12:
        phone_clean = phone_clean[2:]
    if len(phone_clean) > 10:
        phone_clean = phone_clean[-10:]

    if len(phone_clean) == 10:
        output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += "📱 **NUMBER INFORMATION**\n"
        output += f"├ 📞 Number      : {phone_clean}\n"

        url3 = f"{NUM_API}?key={NUM_KEY}&num={phone_clean}"
        try:
            res3 = requests.get(url3, timeout=20)
            if res3.status_code == 200:
                json3 = res3.json()
                num_records = json3.get('response', {}).get('data', [])
                
                if num_records and isinstance(num_records, list):
                    num_data = pick_best_record(num_records, phone_clean)
                    if num_data:
                        n_name = extract_field(num_data, ['name', 'full_name', 'fullname'])
                        n_fname = extract_field(num_data, ['fname', 'father_name', 'father', 'fathername'])
                        n_aadhaar = extract_field(num_data, ['aadhar', 'aadhaar', 'adhar', 'adhaar', 'uid', 'uidai'])
                        n_address = clean_address(extract_field(num_data, ['address', 'addr', 'location']))
                        n_circle = extract_field(num_data, ['circle', 'operator', 'state'])
                        n_email = extract_field(num_data, ['email', 'mail'])
                        n_alt = extract_field(num_data, ['alt', 'alt_number', 'alternate'])

                        output += f"├ 📛 Name        : {n_name}\n"
                        output += f"├ 👨 Father Name : {n_fname}\n"

                        if n_aadhaar != 'N/A' and n_aadhaar:
                            output += f"├ 🪪 Aadhaar     : <code>{format_aadhaar(n_aadhaar)}</code>\n"
                        else:
                            output += "├ 🪪 Aadhaar     : ❌ Not Available\n"

                        output += f"├ 📍 Address     : {n_address}\n"
                        output += f"├ 📡 Circle      : {n_circle}\n"
                        output += f"├ 📧 Email       : {n_email}\n"
                        output += f"└ 📱 Alt Number  : {n_alt}\n\n"
                        output += f"📊 <b>Total {len(num_records)} records found</b>\n"
                    else:
                        output += "└ ❌ Number detail not found in records\n"
                else:
                    output += "└ ❌ Number detail not found\n"
        except Exception as e:
            logger.error(f"API 3 Error: {e}")
            output += "└ ❌ Number info fetch error\n"

    output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    output += "💳 BUY API : @Vectraen\n"
    output += "🆘 SUPPORT : @Vectraen\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if len(output) > 4000:
        output = output[:3950] + "\n\n...[Message Truncated]..."

    await update.message.reply_text(output, parse_mode="HTML")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot started successfully...")
    application.run_polling()

if __name__ == '__main__':
    main()
          
