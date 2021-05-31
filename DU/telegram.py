import telegram
import requests
import json
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def send_telegram(chat_id,config, subject, url):
    bot = telegram.Bot(token=config["account"]["token"])
    reply_markup =[[InlineKeyboardButton(text="바로가기", url=url)]]
    bot.sendMessage(chat_id=chat_id, text=subject, reply_markup=InlineKeyboardMarkup(reply_markup))
