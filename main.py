import locale
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
    articles = soup.find_all("div", class_="content")

    for article in articles:
        date_span = article.find("span", class_="date")
        A = date_span.text
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
        current_time = time.localtime()
        B = time.strftime("%d %B %Y", current_time)

        if A.lower() == B.lower():
            title = article.find('a')['title']
            link = article.find('a')['href']
            return link
        else:
            print("Nessun articolo oggi")


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
    get_latest_article()
