import requests
import json
import emoji
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from config import TOKEN, MAIL_TM_API, GUERRILLA_MAIL_API, DEFAULT_PROVIDER

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
user_data = {}  # Stores users' emails and provider choices

def create_mail_tm():
    """Creates an email using Mail.tm API"""
    response = requests.post(f"{MAIL_TM_API}/accounts", json={})
    return response.json() if response.status_code == 201 else None

def get_inbox_tm():
    """Fetches inbox from Mail.tm"""
    response = requests.get(f"{MAIL_TM_API}/messages")
    return response.json()["hydra:member"] if response.status_code == 200 else []

def create_guerrilla_mail():
    """Creates an email using Guerrilla Mail"""
    response = requests.get(f"{GUERRILLA_MAIL_API}?f=get_email_address")
    return response.json() if response.status_code == 200 else None

def get_inbox_guerrilla():
    """Fetches inbox from Guerrilla Mail"""
    response = requests.get(f"{GUERRILLA_MAIL_API}?f=check_email")
    return response.json()["list"] if response.status_code == 200 else []

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    """Sends the start menu"""
    buttons = [
        InlineKeyboardButton(emoji.emojize("📩 Get Temp Mail"), callback_data="get_mail"),
        InlineKeyboardButton(emoji.emojize("🔄 Change Provider"), callback_data="change_provider"),
        InlineKeyboardButton(emoji.emojize("📥 Check Inbox"), callback_data="check_inbox"),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1).add(*buttons)
    await message.reply("Welcome to the **Temp Mail Bot**!", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == "get_mail")
async def get_mail(callback_query: types.CallbackQuery):
    """Creates a new temporary email"""
    user_id = callback_query.from_user.id
    provider = user_data.get(user_id, DEFAULT_PROVIDER)

    if provider == "mail.tm":
        email_data = create_mail_tm()
    else:
        email_data = create_guerrilla_mail()

    if email_data:
        user_data[user_id] = {
            "email": email_data.get("address", email_data.get("email_addr")),
            "provider": provider
        }
        await bot.send_message(user_id, f"**Your temp email:** `{user_data[user_id]['email']}`", parse_mode="Markdown")
    else:
        await bot.send_message(user_id, "⚠️ Failed to create email. Try again.")

@dp.callback_query_handler(lambda c: c.data == "check_inbox")
async def check_inbox(callback_query: types.CallbackQuery):
    """Checks inbox for new messages"""
    user_id = callback_query.from_user.id
    user_info = user_data.get(user_id)

    if not user_info:
        await bot.send_message(user_id, "⚠️ You need to generate an email first!")
        return

    provider = user_info["provider"]
    inbox = get_inbox_tm() if provider == "mail.tm" else get_inbox_guerrilla()

    if inbox:
        messages = "\n".join([f"📩 *{msg['subject']}*" for msg in inbox[:5]])
        await bot.send_message(user_id, f"📥 **Inbox:**\n{messages}", parse_mode="Markdown")
    else:
        await bot.send_message(user_id, "📭 Inbox is empty.")

@dp.callback_query_handler(lambda c: c.data == "change_provider")
async def change_provider(callback_query: types.CallbackQuery):
    """Switches between Mail.tm and Guerrilla Mail"""
    user_id = callback_query.from_user.id
    current_provider = user_data.get(user_id, {}).get("provider", DEFAULT_PROVIDER)

    new_provider = "guerrilla" if current_provider == "mail.tm" else "mail.tm"
    user_data[user_id] = {"provider": new_provider}
    
    await bot.send_message(user_id, f"✅ Provider changed to **{new_provider.upper()}**")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
