import requests
from bs4 import BeautifulSoup
def get_latest_article(url="https://vulcanostatale.it/"):
    response = None

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("div", class_="content")

    for article in articles:
        date_span = article.find("span", class_="date")
        if date_span:
            article_date = date_span.text.strip().lower()
            if article_date == "31 Luglio 2024":
                title = article.find('a')['title']
                link = article.find('a')['href']
                return link, title

if __name__ == '__main__':
    get_latest_article()