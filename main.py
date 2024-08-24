import locale
import time
from typing import Final

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from credentials import TOKEN, user

# Bot configuration
Token: Final = TOKEN
Bot_username: Final = user

start_text = ("Ciao! Sono 🪨 lapillo 🪨, il Telegram bot di Vulcano Statale, il giornale degli studenti "
              "dell'Università statale di Milano. Se vuoi capire meglio cosa faccio e come interagire "
              "con me, digita /help.")

help_text = ""


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text)


# Responses
def get_latest_article(url="https://vulcanostatale.it/"):
    # Getting today's date
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    current_time = time.localtime()
    today_date = time.strftime("%d %B %Y", current_time).lower()
    # The "%d %B %Y" format is coherent with the one used on vulcanostatale.it: it can be
    # changed accordingly to the user needs.

    # Request to the website
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("div", class_="content")

    for article in articles:
        date_span = article.find("span", class_="date")
        if date_span:
            article_date = date_span.text.strip().lower()
            if article_date == today_date:
                title = article.find('a')['title']
                link = article.find('a')['href']
                return link, title

    return None


def handle_response() -> str:
    if get_latest_article() is None:
        txt = "Ciao 🤖😊🤖. Per ora non c'è nessun nuovo articolo."
        return txt
    else:
        link, title = get_latest_article()
        txt = (f"Ciao 🤖😊🤖, è appena uscito un nuovo articolo sul sito di Vulcano! 🎉 "
               f"Si intitola '**{title}**', e lo puoi trovare qui: {link}. Buona lettura 😊."
               "🪨 lapillo 🪨")
        return txt


async def handle_message(update, context):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == "group":
        if Bot_username in text:
            new_text: str = text.replace(Bot_username, "").strip()
            response: str = handle_response()
        else:
            return
    else:
        response: str = handle_response()

    print(f"Bot, {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == '__main__':
    print("Starting...")
    app = Application.builder().token(Token).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)

    # Polling
    print("Polling...")
    app.run_polling(poll_interval=3)
