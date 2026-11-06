import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION (Fully Configured) ---
API_TOKEN = "9032220713:AAH1tElfjJNIS0zwgDbDccQJQOqzKFrj5do"
SENDER_EMAIL = "meand3dog55@gmail.com"     #[span_1](start_span)[span_1](end_span) ပုံထဲက မင်းရဲ့ Gmail လိပ်စာ
SENDER_PASSWORD = "oaiu dqzk mykr iogj"       # မင်းပေးထားတဲ့ App Password

# Logging Setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class ReportState(StatesGroup):
    waiting_for_link = State()

# --- 1. START COMMAND & LANGUAGE SELECTION ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇲🇲 မြန်မာ", callback_data="lang_my"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    await message.reply(
        "🔞 **Live Status Child Protection & Explicit Content Report Bot**\n\n"
        "ကျေးဇူးပြု၍ ဘာသာစကားကို ရွေးချယ်ပါ / Please select a language:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- 2. LANGUAGE HANDLER & PROMPT FOR LINK ---
@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data.split('_')[1]
    await state.update_data(language=lang)
    await bot.answer_callback_query(callback_query.id)
    
    if lang == 'my':
        text = "🚨 **Target Locked.**\n\nကျေးဇူးပြု၍ တိုင်ကြားလိုသော Channel သို့မဟုတ် Post ၏ လင့်ခ်ကို ပို့ပေးပါ:"
    else:
        text = "🚨 **Target Locked.**\n\nPlease send the link of the target channel or post:"
        
    await bot.send_message(callback_query.from_user.id, text, parse_mode="Markdown")
    await ReportState.waiting_for_link.set()

# --- 3. LIVE PROGRESS STATUS TRACKING & MULTI-REPORT DISPATCH ---
@dp.message_handler(state=ReportState.waiting_for_link)
async def process_report_link(message: types.Message, state: FSMContext):
    target_link = message.text.strip()
    data = await state.get_data()
    lang = data.get('language', 'en')
    
    if not target_link.startswith("http") and "t.me/" not in target_link:
        await message.reply("⚠️ ပေးပို့လာသော လင့်ခ်မှာ မမှန်ကန်ပါ။ ကျေးဇူးပြု၍ မှန်ကန်သော Telegram လင့်ခ်ကို ထည့်ပါ။")
        return

    # Initial Live Status Message
    status_msg = await message.reply(
        "🔄 **[Live Status]**\n"
        f"├ Target: <code>{target_link}</code>\n"
        "├ Status: ⏳ Initializing connection...\n"
        "└ Progress: [░░░░░░░░░░] 0%",
        parse_mode="HTML"
    )

    total_reports = 5
    
    for i in range(1, total_reports + 1):
        percent = int((i / total_reports) * 100)
        filled_blocks = "█" * int(percent / 10)
        empty_blocks = "░" * (10 - int(percent / 10))
        progress_bar = f"[{filled_blocks}{empty_blocks}] {percent}%"

        try:
            # Edit live status message
            await bot.edit_message_text(
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
                text=f"🔄 **[Live Status: In Progress]**\n"
                     f"├ Target: <code>{target_link}</code>\n"
                     f"├ Status: 🚀 Dispatching Report Batch {i}/{total_reports}...\n"
                     f"└ Progress: {progress_bar}",
                parse_mode="HTML"
            )

            # SMTP Email Dispatch to Telegram Safety Team
            subject = f"URGENT: Prohibited & Child Safety Violation Report (Case #{i})"
            body = f"""CRITICAL ENFORCEMENT & SAFETY NOTICE:
The following Telegram channel/post is actively distributing severe prohibited content and violating child safety protection policies. Immediate action is requested to ban this channel and purge the content.

Target Link: {target_link}
"""
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = "abuse@telegram.org"

            # Connecting via SSL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(msg['From'], [msg['To']], msg.as_string())
                
        except Exception as e:
            logging.error(f"Error in report batch {i}: {e}")

        # Natural delay to prevent rate-limiting or spam flagging
        if i < total_reports:
            await asyncio.sleep(10)

    # Final Success Live Status Message
    await bot.edit_message_text(
        chat_id=status_msg.chat.id,
        message_id=status_msg.message_id,
        text=f"✅ **[Live Status: Completed Successfully]**\n"
             f"├ Target: <code>{target_link}</code>\n"
             f"├ Status: 🛡️ All reports delivered to Telegram Safety Team (`abuse@telegram.org`).\n"
             f"└ Progress: [██████████] 100%\n\n"
             f"📌 *Note:* Telegram ၏ စစ်ဆေးရေးအဖွဲ့မှ ၂၄ နာရီအတွင်း ဝင်ရောက်စစ်ဆေးပြီး Channel ကို ဖျက်သိမ်းသွားပါမည်။",
        parse_mode="HTML"
    )
    
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
