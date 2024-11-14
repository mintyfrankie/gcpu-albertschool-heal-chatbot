"""
Worker for Telegram bot
"""

import asyncio
import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
assert token is not None, "TELEGRAM_TOKEN is not set"

bot = AsyncTeleBot(token)


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    text = "Hi, I am EchoBot.\nJust write me something and I will repeat it!"
    await bot.reply_to(message, text)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


asyncio.run(bot.polling())
