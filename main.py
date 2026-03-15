import config
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

async def start(update, context):
    await update.message.reply_text("Бот запущен и готов к работе!")

async def echo(update, context):
    await update.message.reply_text(f"Я получил: {update.message.text}")

if __name__ == '__main__':
    # Прямая инициализация
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("Бот запускается...")
    app.run_polling()
