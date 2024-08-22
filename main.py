import os
import time
from typing import Final

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

from credentials import TOKEN, user

# Bot configuration
Token: Final = TOKEN
Bot_username: Final = user
Group_ID = 'YOUR_GROUP_ID'

start_text = ("Ciao! Sono 🪨 lapillo 🪨, il Telegram bot di Vulcano Statale, il giornale degli studenti "
              "dell'Università statale di Milano")

help_text = ""


# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text)


# Responses
URL = "https://vulcanostatale.it/"


def get_latest_article():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    article = soup.find('article')
    if article:
        title = article.find('h2').get_text()
        link = article.find('a')['href']
        return title, link


def send_message_to_group(message, context):
    context.bot.send_message(chat_id=GROUP_ID, text=message)


def check_for_new_article():
    last_title, last_link = get_latest_article()

    if not last_title or not last_link:
        print("Non è stato trovato nessun articolo.")
        return

    if os.path.exists(LAST_ARTICLE_FILE):
        with open(LAST_ARTICLE_FILE, 'r') as file:
            saved_title = file.read().strip()

        if last_title != saved_title:
            send_message_to_group(f"Nuovo articolo pubblicato: {last_title}\nLeggilo qui: {last_link}")
            with open(LAST_ARTICLE_FILE, 'w') as file:
                file.write(last_title)
    else:
        with open(LAST_ARTICLE_FILE, 'w') as file:
            file.write(last_title)


if __name__ == '__main__':
    while True:
        check_for_new_article()
        time.sleep(86400)  # 86400 secondi = 24 ore
