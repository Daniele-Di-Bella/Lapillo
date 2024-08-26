import locale
import time
from typing import Final

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ConversationHandler, filters, ContextTypes
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


# deepen_command conversation states
WAITING = 1
deepen_text = "Che temi vuoi approfondire? Scrivi alcune parole chiave separate da uno spazio."


async def deepen_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(deepen_text)
    return WAITING  # Passa allo stato WAITING


async def keywords_articles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    separator = "-"
    ini_url = "https://vulcanostatale.it/tag/"
    fin_url = separator.join(update.message.text.split())
    url = ini_url + fin_url

    response = None

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")
        await update.message.reply_text("Errore nella richiesta.")
        return ConversationHandler.END

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("h3", class_="entry-title")

    if not articles:
        await update.message.reply_text("Sembra che su Vulcano non sia stato pubblicato ancora nulla "
                                        "che consenta di approfondire questi temi.")
        return ConversationHandler.END

    link_list = []
    for article in articles:
        title = article.find('a').text
        link = article.find('a')['href']
        link_list.append(f"• {title}: {link}")

    final_text = "\n".join(link_list)
    await update.message.reply_text(final_text)
    return ConversationHandler.END


def get_latest_article(url="https://vulcanostatale.it/"):
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    current_time = time.localtime()
    today_date = time.strftime("%d %B %Y", current_time).lower()

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


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == '__main__':
    print("Starting...")
    app = Application.builder().token(Token).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('deepen', deepen_command)],
        states={
            WAITING: [MessageHandler(filters.TEXT & ~filters.COMMAND, keywords_articles)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)

    # Error
    app.add_error_handler(error)

    # Polling
    print("Polling...")
    app.run_polling(poll_interval=3)
