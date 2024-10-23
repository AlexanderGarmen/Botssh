from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import subprocess
import psutil
import asyncio
import nest_asyncio
import time

nest_asyncio.apply()

# Your bot token
TOKEN = 'YOUR_BOT_TOKEN'
AUTHORIZED_USER_ID =   # Replace with your Telegram ID

async def start(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("You don't have permission to use this bot.")
        return

    keyboard = [
        [InlineKeyboardButton("Enable SSH", callback_data='enable_ssh')],
        [InlineKeyboardButton("Disable SSH", callback_data='disable_ssh')],
        [InlineKeyboardButton("Reboot Server", callback_data='reboot_server')],
        [InlineKeyboardButton("Server Info", callback_data='server_info')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose an action:', reply_markup=reply_markup)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.from_user.id != AUTHORIZED_USER_ID:
        await query.edit_message_text("You don't have permission to use this bot.")
        return

    if query.data == 'enable_ssh':
        result = manage_ssh('start')
        await query.edit_message_text(text=f"SSH enabled.\n{result}")
    elif query.data == 'disable_ssh':
        result = manage_ssh('stop')
        await query.edit_message_text(text=f"SSH disabled.\n{result}")
    elif query.data == 'reboot_server':
        result = reboot_server()
        await query.edit_message_text(text=f"Server rebooting.\n{result}")
    elif query.data == 'server_info':
        info = get_server_info()
        await query.edit_message_text(text=f"Server Info:\n{info}")

def manage_ssh(action: str) -> str:
    try:
        subprocess.run(['sudo', 'systemctl', action, 'ssh'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.decode()}"

def reboot_server() -> str:
    try:
        subprocess.run(['sudo', 'reboot'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "Reboot command executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.decode()}"

def get_server_info() -> str:
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    uptime = get_uptime()

    info = (
        f"CPU Usage: {cpu_usage}%\n"
        f"Memory Usage: {memory.percent}%\n"
        f"Free Memory: {memory.available / (1024 ** 2):.2f} MB\n"
        f"Total Memory: {memory.total / (1024 ** 2):.2f} MB\n"
        f"Server Uptime: {uptime}"
    )
    return info

def get_uptime() -> str:
    uptime_seconds = time.time() - psutil.boot_time()
    
    days = uptime_seconds // (24 * 3600)
    uptime_seconds = uptime_seconds % (24 * 3600)
    hours = uptime_seconds // 3600
    uptime_seconds %= 3600
    minutes = uptime_seconds // 60
    seconds = uptime_seconds % 60
    
    uptime_str = f"{int(days)} days {int(hours)} hrs, {int(minutes)} mins {int(seconds)} secs"
    return uptime_str

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
